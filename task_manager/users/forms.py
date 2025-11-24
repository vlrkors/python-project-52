from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserCreateForm(UserCreationForm):
    password1 = forms.CharField(
        required=True,
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Password"),
            }
        ),
        help_text=_("Your password must contain at least 3 characters."),
    )
    password2 = forms.CharField(
        required=True,
        label=_("Confirm Password"),
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Confirm Password"),
            }
        ),
        help_text=_("Enter the same password again for verification."),
    )

    label_suffix = ""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "password1",
            "password2",
        ]
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "username": "Имя пользователя",
        }
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "required": True,
                    "placeholder": "Имя",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "required": True,
                    "placeholder": "Фамилия",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "required": True,
                    "placeholder": "Имя пользователя",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                self.add_error("password2", _("Passwords do not match."))

            if len(password1) < 3:
                self.add_error(
                    "password2",
                    _(
                        "The entered password is too short. \
                        It must contain at least 3 characters."
                    ),
                )
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class UserRegistrationForm(UserCreateForm):
    pass


class UserUpdateForm(UserCreateForm):
    def clean_username(self):
        username = self.cleaned_data.get("username")

        if username == self.instance.username:
            return username

        if (
            User.objects.filter(username=username)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError(
                User._meta.get_field("username").error_messages["unique"]
            )

        return username


class UserLoginForm(AuthenticationForm):
    label_suffix = ""
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Username"),
            }
        ),
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Password"),
            }
        ),
    )
