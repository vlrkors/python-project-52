from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

try:
    from rollbar.contrib.django.middleware import RollbarNotifierMiddleware
except Exception:  # pragma: no cover
    class RollbarNotifierMiddleware(MiddlewareMixin):
        """Базовый no-op middleware, когда rollbar недоступен."""

        def __init__(self, get_response=None):
            super().__init__(get_response)

        def process_exception(self, request, exception):  # noqa: D401
            # Нам некуда отправлять ошибки без rollbar.
            # Просто продолжаем цепочку.
            return None


class CustomRollbarNotifierMiddleware(RollbarNotifierMiddleware):
    def __init__(self, get_response=None):
        rollbar_settings = getattr(settings, 'ROLLBAR', {}) or {}

        if not rollbar_settings.get('access_token'):
            # Если токен не задан, пропускаем инициализацию rollbar,
            # но оставляем middleware рабочим (например, в тестах).
            MiddlewareMixin.__init__(self, get_response)
            self.settings = rollbar_settings
            return

        super().__init__(get_response)

    def get_extra_data(self, request, exc):
        return {"feature_flags": ["feature_1", "feature_2"]}

    def get_payload_data(self, request, exc):
        payload_data = dict()
        if not request.user.is_anonymous:
            payload_data['person'] = {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
            }
        return payload_data
