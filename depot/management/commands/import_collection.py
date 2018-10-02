from Converter.bspt.reader import bsp2json
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from depot.models import Collection
from depot.utils import OSType, OSTypeString, parse_ledi, parse_resources

import os
import re


class Command (BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('files', nargs='+')

    def handle(self, *args, **options):
        for f in options['files']:
            collection_tag = None
            resources = []
            levels = []
            rsrc_data = open(f, 'rb').read()
            # This would be way more efficient if we didn't need to parse the LEDI to get the collection tag.
            for tag, num, name, data in parse_resources(rsrc_data):
                filename = re.sub(r'[^a-z0-9\-\.]', '', name or 'untitled', flags=re.I)
                resources.append((tag, num, name, data))
                print(OSTypeString(tag), num, name, len(data))
                if tag == OSType('LEDI') and num == 128:
                    for set_tag, level_tag, name, intro, rsrc_name in parse_ledi(data):
                        collection_tag = set_tag
                        levels.append((level_tag, name.strip(), intro.replace('\r', '\n').strip(), rsrc_name))
                        print('  -', OSTypeString(set_tag), OSTypeString(level_tag), name, rsrc_name)
            # Make this an option.
            Collection.objects.filter(tag=collection_tag).delete()
            name = os.path.basename(f).rsplit('.', 1)[0]
            collection = Collection.objects.create(tag=collection_tag, name=name, slug=slugify(name),
                original=ContentFile(rsrc_data, name=os.path.basename(f)))
            name_map = {}
            for tag, num, name, data in resources:
                name_map[name] = collection.resources.create(tag=tag, num=num, name=name,
                    data=ContentFile(data, name=filename))
                if tag == OSType('BSPT'):
                    name_map[name].alts.create(slug='json', mimetype='application/json', data=bsp2json(data))
                # TODO: store image/svg+xml for PICTs?
            for level_tag, name, intro, rsrc_name in levels:
                collection.levels.create(tag=level_tag, name=name, slug=slugify(name), description=intro,
                    pict=name_map[rsrc_name])
