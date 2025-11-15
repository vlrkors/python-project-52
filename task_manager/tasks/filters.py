import django_filters
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from task_manager.labels.models import Label
from task_manager.statuses.models import Status

from .models import Task

User = get_user_model()


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        label=_("Status")
    )
    executor = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label=_("Executor")
    )
    labels = django_filters.ModelChoiceFilter(
        queryset=Label.objects.all(),
        label=_("Label")
    )

    class Meta:
        model = Task
        fields = ['status', 'executor', 'labels']
