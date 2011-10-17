from django import forms

class UserLoginForm(forms.Form):
	username = forms.CharField(max_length=30, label='User name')
	password = forms.CharField(max_length=128, widget=forms.PasswordInput, label='Password')
