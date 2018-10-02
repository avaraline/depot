from django.db import models
from django.urls import reverse
from django.utils import timezone

from .utils import OSType, OSTypeString

import os


class Server (models.Model):
    address = models.GenericIPAddressField()
    port = models.IntegerField()
    last_seen = models.DateTimeField(default=timezone.now)
    players = models.TextField()
    description = models.TextField(blank=True)

    class Meta:
        unique_together = [
            ('address', 'port'),
        ]

    def update(self, data):
        self.last_seen = timezone.now()
        self.players = '\n'.join(data.get('players', []))
        self.description = data.get('description', '')
        self.save()

    def to_dict(self, **extra):
        return {
            'address': self.address,
            'port': self.port,
            'last_seen': self.last_seen.isoformat(),
            'players': [p.strip() for p in self.players.split('\n') if p.strip()],
            'description': self.description.strip(),
            **extra
        }


class SlugOrTagManager (models.Manager):

    def find(self, slug_or_tag, **extra):
        if isinstance(slug_or_tag, int) or slug_or_tag.isdigit():
            # If slug_or_tag is a number, it's clearly a tag.
            return self.model.objects.get(tag=slug_or_tag, **extra)
        elif len(slug_or_tag) == 4:
            # If slug_or_tag is 4 characters, it's *probably* an OSType, but not certainly.
            try:
                return self.model.objects.get(tag=OSType(slug_or_tag), **extra)
            except self.model.DoesNotExist:
                return self.model.objects.get(slug=slug_or_tag, **extra)
        else:
            # Otherwise, we're just looking for a slug.
            return self.model.objects.get(slug=slug_or_tag, **extra)


def original_path(instance, filename):
    return os.path.join('originals', filename)


class Collection (models.Model):
    tag = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    original = models.FileField(upload_to=original_path)

    objects = SlugOrTagManager()

    ostype = property(lambda self: OSTypeString(self.tag))

    def __str__(self):
        return self.name

    def api_url(self):
        return reverse('api-v1-collection', kwargs={
            'slug': self.slug,
        })

    def to_dict(self, **extra):
        return {
            'name': self.name,
            'tag': self.ostype,
            'uri': self.api_url(),
            'download_uri': reverse('api-v1-resource', kwargs={
                'slug': self.slug,
            }),
            **extra
        }


def resource_path(instance, filename):
    return os.path.join(
        OSTypeString(instance.collection.tag),
        OSTypeString(instance.tag),
        '{}-{}'.format(instance.num, filename)
    )


class Resource (models.Model):
    collection = models.ForeignKey(Collection, related_name='resources', on_delete=models.CASCADE)
    tag = models.IntegerField()
    num = models.IntegerField()
    name = models.CharField(max_length=255, blank=True)
    data = models.FileField(upload_to=resource_path)

    ostype = property(lambda self: OSTypeString(self.tag))
    path = property(lambda self: self.data.name)

    class Meta:
        unique_together = [
            ('collection', 'tag', 'num')
        ]

    def __str__(self):
        return self.name or str(self.num)

    def api_url(self):
        return reverse('api-v1-resource-num', kwargs={
            'slug': self.collection.slug,
            'tag': self.ostype,
            'num': self.num,
        })

    def to_dict(self, **extra):
        return {
            'name': self.name,
            'tag': self.ostype,
            'num': self.num,
            'uri': self.api_url(),
            **extra
        }


class ResourceAlt (models.Model):
    resource = models.ForeignKey(Resource, related_name='alts', on_delete=models.CASCADE)
    slug = models.SlugField()
    mimetype = models.CharField(max_length=100)
    data = models.TextField()


class Level (models.Model):
    collection = models.ForeignKey(Collection, related_name='levels', on_delete=models.CASCADE)
    tag = models.IntegerField()
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    pict = models.ForeignKey(Resource, related_name='levels', on_delete=models.CASCADE)

    objects = SlugOrTagManager()

    ostype = property(lambda self: OSTypeString(self.tag))

    class Meta:
        unique_together = [
            ('collection', 'tag'),
            ('collection', 'slug'),
        ]

    def __str__(self):
        return self.name

    def api_url(self):
        return reverse('api-v1-level', kwargs={
            'slug': self.collection.slug,
            'level': self.slug,
        })

    def to_dict(self, **extra):
        return {
            'name': self.name,
            'tag': self.ostype,
            'description': self.description,
            'uri': self.api_url(),
            'pict_uri': self.pict.api_url(),
            **extra
        }
