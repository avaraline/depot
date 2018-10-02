from django.contrib import admin
from django.urls import include, path

from . import api


urlpatterns = [
    path('api/v1/', include([
        path('tracker/', api.TrackerAPI.as_view(), name='api-v1-tracker'),
        path('search/', api.SearchAPI.as_view(), name='api-v1-search'),
        path('collection/<slug>/', api.CollectionAPI.as_view(), name='api-v1-collection'),
        path('level/<slug>/<level>/', api.LevelAPI.as_view(), name='api-v1-level'),
        path('resource/<slug>/<tag>/<num>/', api.ResourceAPI.as_view(), name='api-v1-resource'),
        path('resource/<slug>/<tag>/<num>/<alt>/', api.ResourceAPI.as_view(), name='api-v1-resource-alt'),
    ])),
    path('admin/', admin.site.urls),
]
