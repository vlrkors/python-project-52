from __future__ import annotations

from typing import Any, Mapping, Tuple, Union

from django.utils.encoding import force_str

default_app_config = "django_bootstrap5.apps.Bootstrap5Config"


def text_value(value: Any) -> str:
    """Return a string representation of the value (empty string for None)."""
    if value is None:
        return ""
    return force_str(value)


def get_url_attrs(
    value: Union[str, Mapping[str, Any], Tuple[Any, Mapping[str, Any]]],
    *,
    attr_name: str = "href",
) -> dict[str, str]:
    """
    Build attribute dict for script/link tags.

    Accepts either a string URL, a mapping with extra attributes, or a tuple
    (url, extra_attributes).
    The requested attribute name is stored with the URL.
    """
    attrs: dict[str, str] = {}
    url: Any = value
    extra_attrs: Mapping[str, Any] | None = None

    if isinstance(value, tuple) and len(value) == 2:
        url, extra_attrs = value
    elif isinstance(value, Mapping):
        mapping = dict(value)
        url = mapping.pop("url", mapping.pop(attr_name, url))
        extra_attrs = mapping

    if extra_attrs:
        for key, attr in extra_attrs.items():
            if attr is not None:
                attrs[key] = text_value(attr)

    if not url:
        return attrs

    attrs[attr_name] = text_value(url)
    return attrs


__all__ = [
    "text_value",
    "get_url_attrs",
]
