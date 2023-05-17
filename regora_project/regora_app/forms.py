from django import forms

class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=True)
    last_name = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(max_length=50, required=True)
    password = forms.CharField(max_length=20, widget=forms.PasswordInput, required=True)
    phone_number = forms.CharField(max_length=11, required=True)

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
