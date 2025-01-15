from django import forms
from .models import Team

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=50)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)
    

class TeamCreationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'
