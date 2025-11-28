import pytest
from django.forms import Select, SelectMultiple, Textarea, TextInput

from task_manager.labels.forms import LabelForm
from task_manager.statuses.forms import StatusForm
from task_manager.tasks.forms import TaskForm


@pytest.mark.django_db
def test_label_form_widget_attrs_and_label_suffix():
    form = LabelForm()
    assert form.label_suffix == ""
    name_field = form.fields["name"]
    widget = name_field.widget
    assert isinstance(widget, TextInput)
    assert widget.attrs["class"] == "form-control"
    placeholder = widget.attrs.get("placeholder")
    assert placeholder == name_field.label


@pytest.mark.django_db
def test_status_form_widget_attrs_and_label_suffix():
    form = StatusForm()
    assert form.label_suffix == ""
    name_field = form.fields["name"]
    widget = name_field.widget
    assert isinstance(widget, TextInput)
    assert widget.attrs["class"] == "form-control"
    placeholder = widget.attrs.get("placeholder")
    assert placeholder == name_field.label


@pytest.mark.django_db
def test_task_form_fields_and_widgets():
    form = TaskForm()
    assert form.label_suffix == ""
    assert list(form.fields) == [
        "name",
        "description",
        "status",
        "executor",
        "labels",
    ]

    assert isinstance(form.fields["name"].widget, TextInput)
    assert form.fields["name"].widget.attrs["class"] == "form-control"

    description_widget = form.fields["description"].widget
    assert isinstance(description_widget, Textarea)
    assert description_widget.attrs["rows"] == 3

    assert isinstance(form.fields["status"].widget, Select)
    assert form.fields["status"].widget.attrs["class"] == "form-select"

    assert isinstance(form.fields["executor"].widget, Select)
    assert form.fields["executor"].widget.attrs["class"] == "form-select"

    assert isinstance(form.fields["labels"].widget, SelectMultiple)
    assert form.fields["labels"].widget.attrs["class"] == "form-select"
