from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Profile, Enveloppe



class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

class CSV_load(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['user_data'] 

class Indicateurs_load(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['indicateurs_data'] 

class Enveloppe_form(forms.ModelForm):
	class Meta:
		model = Enveloppe
		exclude = ['user']