try:
    from rollbar.contrib.django.middleware import RollbarNotifierMiddleware
except Exception:  # pragma: no cover
    # rollbar и его зависимости могут отсутствовать в окружении.
    from django.utils.deprecation import MiddlewareMixin

    class RollbarNotifierMiddleware(MiddlewareMixin):
        """Базовый no-op middleware, когда rollbar недоступен."""

        def __init__(self, get_response=None):
            super().__init__(get_response)

        def process_exception(self, request, exception):  # noqa: D401
            # Нам некуда отправлять ошибки без rollbar.
            # Просто продолжаем цепочку.
            return None


class CustomRollbarNotifierMiddleware(RollbarNotifierMiddleware):
    def get_extra_data(self, request, exc):
        extra_data = dict()
        extra_data['feature_flags'] = ['feature_1', 'feature_2']
        return extra_data

    def get_payload_data(self, request, exc):
        payload_data = dict()
        if not request.user.is_anonymous:
            payload_data['person'] = {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
            }
        return payload_data
