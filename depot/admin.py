from django.contrib import admin

from .models import Collection, Level, Resource, ResourceAlt, Server


@admin.register(Server)
class ServerAdmin (admin.ModelAdmin):
    list_display = ('address', 'port', 'last_seen', 'players', 'description')


@admin.register(Collection)
class CollectionAdmin (admin.ModelAdmin):
    list_display = ('name', 'slug', 'ostype')
    ordering = ('name',)


class ResourceAltInline (admin.TabularInline):
    model = ResourceAlt
    extra = 0


@admin.register(Resource)
class ResourceAdmin (admin.ModelAdmin):
    list_display = ('path', 'collection', 'ostype', 'num', 'name')
    list_filter = ('collection',)
    ordering = ('data',)
    inlines = (ResourceAltInline,)


@admin.register(Level)
class LevelAdmin (admin.ModelAdmin):
    list_display = ('name', 'slug', 'collection', 'ostype', 'description')
    list_filter = ('collection',)
    ordering = ('name',)
