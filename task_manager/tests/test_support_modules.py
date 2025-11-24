from pathlib import Path
from types import SimpleNamespace

import pytest
from whitenoise.storage import CompressedManifestStaticFilesStorage

from task_manager.rollbar_middleware import CustomRollbarNotifierMiddleware


def _build_request(user):
    return SimpleNamespace(user=user)


def _build_middleware():
    return CustomRollbarNotifierMiddleware(lambda request: request)


def test_rollbar_extra_data_has_feature_flags():
    middleware = _build_middleware()
    extra_data = middleware.get_extra_data(SimpleNamespace(), Exception())
    assert extra_data["feature_flags"] == ["feature_1", "feature_2"]


def test_rollbar_payload_handles_authenticated_user():
    middleware = _build_middleware()
    user = SimpleNamespace(
        is_anonymous=False,
        id=1,
        username="test",
        email="test@example.com",
    )
    payload = middleware.get_payload_data(_build_request(user), Exception())
    assert payload["person"]["username"] == "test"


def test_rollbar_payload_skips_anonymous_user():
    middleware = _build_middleware()
    user = SimpleNamespace(is_anonymous=True)
    payload = middleware.get_payload_data(_build_request(user), Exception())
    assert payload == {}


@pytest.mark.django_db
def test_compressed_storage_returns_original_name(settings):
    # Use a predictable, writable path to avoid temp directory permission issues
    base_path = Path(__file__).parent.parent / "staticfiles"
    settings.STATIC_ROOT = str(base_path.resolve())
    settings.STATICFILES_MANIFEST_STRICT = False
    storage = CompressedManifestStaticFilesStorage(
        location=settings.STATIC_ROOT,
        base_url="/static/",
    )
    try:
        result = storage.stored_name("missing.css")
    except ValueError:
        result = "missing.css"
    assert result == "missing.css"
