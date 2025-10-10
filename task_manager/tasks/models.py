from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from task_manager.labels.models import Label
from task_manager.statuses.models import Status

User = get_user_model()


class Task(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    description = models.TextField(blank=True, verbose_name="Описание")
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        verbose_name=_('Status'),
        related_name="tasks"
    )
    labels = models.ManyToManyField(
        Label,
        related_name='tasks',
        blank=True,
        verbose_name=_('Labels')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_('Author'),
        related_name="authored_tasks"
    )
    executor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_('Executor'),
        related_name="executed_tasks",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Creation date')
        )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
