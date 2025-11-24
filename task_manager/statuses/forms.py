from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from task_manager.forms import NoLabelSuffixMixin

from .models import Status


class StatusForm(NoLabelSuffixMixin, ModelForm):
    label_suffix = ""

    class Meta:
        model = Status
        fields = ["name"]
        labels = {"name": _("Name")}
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Name"),
                },
            ),
        }
