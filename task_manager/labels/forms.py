from django import forms
from django.utils.translation import gettext_lazy as _

from task_manager.forms import NoLabelSuffixMixin

from .models import Label


class LabelForm(NoLabelSuffixMixin, forms.ModelForm):
    label_suffix = ""

    class Meta:
        model = Label
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
