from django import forms
from .models import *

class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=True)
    last_name = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(max_length=50, required=True)
    password = forms.CharField(max_length=20, widget=forms.PasswordInput, required=True)
    phone_number = forms.CharField(max_length=11, required=True)

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class ReservationForm(forms.ModelForm):
    guest = forms.ModelChoiceField(queryset=Guest.objects.all(), required=True)
    room = forms.ModelChoiceField(queryset=Room.objects.all(), required=True)
    begin_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    services = forms.ModelMultipleChoiceField(queryset=Service.objects.all(), widget=forms.CheckboxSelectMultiple())
    pickup_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    dropoff_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Reservation
        fields = ['guest', 'room', 'begin_date', 'end_date', 'services', 'pickup_time', 'dropoff_time']