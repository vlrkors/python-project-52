from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from task_manager.labels.models import Label
from task_manager.statuses.models import Status

from .models import Task

User = get_user_model()


class TaskFilterForm(forms.Form):
    status = forms.ModelChoiceField(
        queryset=Status.objects.all(),
        label=_("Status"),
        required=False,
    )
    executor = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label=_("Executor"),
        required=False,
    )
    labels = forms.ModelChoiceField(
        queryset=Label.objects.all(),
        label=_("Label"),
        required=False,
    )


class TaskFilter:
    """Простая подмена django-filter, достаточная для тестов проекта."""

    def __init__(self, data=None, queryset=None):
        self.queryset = (
            queryset if queryset is not None else Task.objects.none()
        )
        self.form = TaskFilterForm(data or None)
        self._qs = self._apply_filters()

    def _apply_filters(self):
        if self.form.is_bound:
            if not self.form.is_valid():
                return self.queryset
            cleaned_data = self.form.cleaned_data
        else:
            cleaned_data = {}
        queryset = self.queryset

        status = cleaned_data.get("status")
        if status:
            queryset = queryset.filter(status=status)

        executor = cleaned_data.get("executor")
        if executor:
            queryset = queryset.filter(executor=executor)

        label = cleaned_data.get("labels")
        if label:
            queryset = queryset.filter(labels=label)

        return queryset

    @property
    def qs(self):
        return self._qs
