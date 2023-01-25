from django import forms

from .models import User


class UserAvatarForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('avatar',)
