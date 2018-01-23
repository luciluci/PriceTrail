from django import forms

class LoginForm(forms.Form):
    username = forms.TextInput()
    password = forms.PasswordInput()