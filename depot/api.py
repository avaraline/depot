from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.http.response import HttpResponseBase
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.views.decorators.gzip import gzip_page
from django.views.generic import View

from .models import Collection, Level, Server
from .utils import OSType

import json


class APIView (View):

    @method_decorator(gzip_page)
    def dispatch(self, request, *args, **kwargs):
        try:
            result = super().dispatch(request, *args, **kwargs)
            if isinstance(result, HttpResponseBase):
                return result
            return JsonResponse(result, json_dumps_params={'indent': 4})
        except (Http404, ObjectDoesNotExist):
            return JsonResponse({'error': 'Record not found.'}, status=404)
        except Exception as ex:
            return JsonResponse({'error': force_text(ex)}, status=500)


class TrackerAPI (APIView):

    def request_ip(self, request):
        try:
            return request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
        except:
            return request.META['REMOTE_ADDR']

    def get(self, request):
        return {
            'servers': [s.to_dict() for s in Server.objects.all()],
        }

    def post(self, request):
        data = json.loads(request.body)
        ip = self.request_ip(request)
        port = int(data.get('port', 19567))
        server, created = Server.objects.get_or_create(address=ip, port=port)
        server.update(data)
        return server.to_dict()


class SearchAPI (APIView):

    def get(self, request):
        q = request.GET.get('q', '').strip()
        levels = Level.objects.filter(Q(name__icontains=q) | Q(collection__name__icontains=q)).select_related('collection') if q else []
        return {
            'levels': [level.to_dict(collection=level.collection.to_dict()) for level in levels],
        }


class CollectionAPI (APIView):

    def get(self, request, slug):
        collection = Collection.objects.find(slug)
        return collection.to_dict(levels=[level.to_dict() for level in collection.levels.all()])


class LevelAPI (APIView):

    def get(self, request, slug, level):
        collection = Collection.objects.find(slug)
        level = Level.objects.find(level, collection=collection)
        return level.to_dict(collection=collection.to_dict())


class ResourceAPI (APIView):

    def get(self, request, slug, tag, num, alt=None):
        if not tag.isdigit():
            if len(tag) != 4:
                raise Exception('Invalid resource tag.')
            tag = OSType(tag)
        collection = Collection.objects.find(slug)
        params = {'num': num} if num.isdigit() else {'name': num}
        resource = collection.resources.get(tag=tag, **params)
        if alt:
            alt = resource.alts.get(slug=alt)
            return HttpResponse(alt.data, content_type=alt.mimetype)
        else:
            return FileResponse(resource.data, as_attachment=True)
