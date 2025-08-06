from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(label='Parol', widget = forms.PasswordInput)
    password2 = forms.CharField(label='Parol', widget= forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        help_texts = {
            'username': ''
        }
    def clean_password2(self):
        password2 = self.cleaned_data["password2"]
        password1 = self.cleaned_data['password1']
        if password2 is None or password1 is None or password1 != password2:
            raise forms.ValidationError('Passwords are not valid')
        return password2

    def save(self, commit = True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password2'])
        if commit:
            user.save()
        return user

class LoginForm (AuthenticationForm):
    username = forms.CharField(max_length=120, label='Login')
    password = forms.CharField(label='Parol', widget = forms.PasswordInput)


class ChangePassForm(forms.Form):
    new_pass = forms.CharField(label="Yangi parol", widget=forms.PasswordInput)
    confirm_pass = forms.CharField(label="Parolni tasdiqlang", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        pass1 = cleaned_data.get('new_pass')
        pass2 = cleaned_data.get('confirm_pass')

        if pass1 != pass2:
            raise forms.ValidationError("Parollar mos emas!")
        return cleaned_data

class ResetPassForm(forms.Form):
    password = forms.CharField(label='Yangi parol' , widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Yangi parolni tasdiqlang !' , widget=forms.PasswordInput)
    code = forms.CharField(label='Tasdiqlash kodi ' ,max_length=6)

    def clean(self):
        cleane_data = super().clean()
        password = self.cleaned_data['password']
        password_confirm = self.cleaned_data['password_confirm']
        if password != password_confirm:
            raise forms. ValidationError('Passwords do not match')
        return cleane_data


class CustomChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Joriy parolingizni kiriting'}),
        label="Joriy parol"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Yangi parol kiriting'}),
        label="Yangi parol",
        help_text="Parol kamida 8 belgidan iborat bo'lishi kerak"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Yangi parolni takrorlang'}),
        label="Yangi parolni tasdiqlang"
    )
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Emailga kelgan kod'}),
        label="Tasdiqlash kodi"
    )

    def clean(self):
        cleaned_data = super().clean()
        new1 = cleaned_data.get('new_password1')
        new2 = cleaned_data.get('new_password2')

        if new1 and new2 and new1 != new2:
            raise forms.ValidationError("Yangi parollar mos kelmadi!")

        if new1:
            try:
                validate_password(new1)
            except ValidationError as e:
                raise forms.ValidationError(e.messages[0])

        return cleaned_data