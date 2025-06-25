from django import forms
from accounts.models import CustomUser
from django.contrib.auth.forms import ReadOnlyPasswordHashField


# NOTE: password fields are always rendered, JS handles dynamic visibility in admin.py
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        required=False
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type')

    def clean_user_type(self):
        user_type = self.cleaned_data.get("user_type")
        if user_type not in [CustomUser.CREATOR, CustomUser.PARTICIPANT]:
            raise forms.ValidationError("Invalid user type.")
        return user_type

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if user_type == CustomUser.CREATOR:
            if not password1 or not password2:
                raise forms.ValidationError("Password is required for creators.")
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        if user.user_type == CustomUser.PARTICIPANT:
            user.set_unusable_password()
            user.is_active = False
        else:
            password = self.cleaned_data.get("password1")
            if password:
                user.set_password(password)
            else:
                user.set_unusable_password()

        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label="Password", required=False)
    password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput,
        required=False
    )
    password2 = forms.CharField(
        label='Confirm new password',
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'is_active', 'is_staff', 'is_superuser')

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        user_type = cleaned_data.get('user_type')

        if user_type == CustomUser.CREATOR:
            # Required when there's no usable password
            if not self.instance.has_usable_password():
                if not password1 or not password2:
                    raise forms.ValidationError("Password is required for creator accounts.")
            # Check match if either is filled
            if password1 or password2:
                if password1 != password2:
                    raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        if user.user_type == CustomUser.PARTICIPANT:
            user.set_unusable_password()
            user.is_active = False
        else:
            password = self.cleaned_data.get('password1')
            if password:
                user.set_password(password)
            elif not user.has_usable_password():
                user.set_unusable_password()

        if commit:
            user.save()
        return user
