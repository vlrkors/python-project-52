from django.utils.deprecation import MiddlewareMixin


class WhiteNoiseMiddleware(MiddlewareMixin):
    """Простая заглушка, не вмешивается в обработку запросов."""

    def __init__(self, get_response=None):
        super().__init__(get_response)

    def __call__(self, request):
        response = None
        if self.get_response is not None:
            response = self.get_response(request)
        return response

