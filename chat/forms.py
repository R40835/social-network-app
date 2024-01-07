from django import forms
from .models import Room


class RoomForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chat Room Name'})
    )
    topic = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optionally add a topic'})
    )

    class Meta:

        model = Room
        fields = ('name', 'topic')
