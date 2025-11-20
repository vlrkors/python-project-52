from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        raise Exception("Rollbar test")
        return super().get(request, *args, **kwargs)

