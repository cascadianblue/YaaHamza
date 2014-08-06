from django.db.models.query import QuerySet
from django.forms import model_to_dict
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin
import json
from django.http import HttpResponse


def jsonify(old):
    def new(*args, **kwargs):
        return HttpResponse(json.dumps(make_jsonable(old(*args, **kwargs))))
    return new


def make_jsonable(data):
    if type(data) in (QuerySet, list, tuple):
        return [make_jsonable(i) for i in data]
    if hasattr(data, 'jsonable'):
        return data.jsonable()
    return model_to_dict(data)


class JsonResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_response(self, data, **response_kwargs):
        """
        Returns a JSON response, transforming 'data' to make the payload.
        """
        return HttpResponse(  # TODO: Change to JsonResponse when django 1.7 is released
            self.data_to_json(data),
            content_type='application/json',
            **response_kwargs
        )

    def data_to_json(self, data):
        """
        Convert the data into a JSON object
        """
        try:
            return self.iterator_to_json(data)
        except TypeError:
            return self.instance_to_json(data)

    def instance_to_json(self, instance):
        """
        Converts a model instance to JSON
        :rtype : str
        """
        if hasattr(instance, 'make_jsonable'):
            return json.dumps(instance.jsonable())
        else:
            return json.dumps(model_to_dict(instance))

    def iterator_to_json(self, iterator):
        return json.dumps([self.instance_to_json(instance) for instance in iterator])


class SingleView(JsonResponseMixin, SingleObjectMixin, View):
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.render_to_response(instance)


class MultipleView(JsonResponseMixin, MultipleObjectMixin, View):
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return self.render_to_response(queryset)