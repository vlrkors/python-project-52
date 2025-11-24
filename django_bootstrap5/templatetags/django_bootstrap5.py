from django import template
from django.contrib.messages import get_messages
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def bootstrap_css():
    """Stub for Bootstrap CSS include."""
    return ""


@register.simple_tag
def bootstrap_javascript():
    """Stub for Bootstrap JS include."""
    return ""


@register.simple_tag(takes_context=True)
def bootstrap_messages(context):
    request = context.get("request")
    if request is None:
        return ""

    pieces = [
        format_html(
            '<div class="alert alert-info" role="alert">{}</div>',
            message,
        )
        for message in get_messages(request)
    ]
    return mark_safe("".join(pieces))


@register.simple_tag
def bootstrap_form(form):
    if form is None:
        return ""
    return mark_safe(form.as_p())


@register.simple_tag
def bootstrap_field(field, show_label=False):
    if field is None:
        return ""

    fragments = []
    if show_label:
        label = field.label_tag(attrs={"class": "form-label"})
        if label:
            fragments.append(label)

    widget_html = field.as_widget(
        attrs={
            "class": (
                "form-select"
                if getattr(field.field, "queryset", None)
                else "form-control"
            )
        },
    )
    fragments.append(widget_html)

    if field.help_text:
        fragments.append(
            format_html('<div class="form-text">{}</div>', field.help_text),
        )

    if field.errors:
        error_text = ", ".join(field.errors)
        fragments.append(
            format_html('<div class="text-danger small">{}</div>', error_text),
        )

    return mark_safe("".join(str(fragment) for fragment in fragments))


@register.simple_tag
def bootstrap_button(label, button_type="submit", button_class="btn-primary"):
    classes = (
        button_class if "btn" in button_class else f"btn {button_class}".strip()
    )
    return format_html(
        '<button type="{}" class="{}">{}</button>',
        button_type,
        classes,
        label,
    )
