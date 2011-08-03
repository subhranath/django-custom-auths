from django import forms

class LoginForm(forms.Form):
    """Login form.
    """
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.widgets.PasswordInput(), required=True)
