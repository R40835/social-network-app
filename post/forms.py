from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Post, Comment


class PostForm(forms.ModelForm):

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell us what\'s on your mind.'})
    )
    
    class Meta:
        model = Post
        fields = ['description', 'photo']

    def clean(self):
        cleaned_data = super().clean()
        description = cleaned_data['description']
        photo = cleaned_data['photo']

        if not description and not photo:
            raise forms.ValidationError("Provide at least a description or a photo.")

        return cleaned_data


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text']


class UpdatePostForm(forms.ModelForm):

    photo = forms.ImageField(
        widget=forms.FileInput,
        required=False
    ) 
    clear_photo = forms.BooleanField(
        required=False
    )

    class Meta():
        model = Post
        fields = ['description', 'photo']

    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.date_created = timezone.now() 

        if commit:
            instance.save()

        return instance


class UpdateCommentForm(forms.ModelForm):

    class Meta():
        model = Comment
        exclude = ['user', 'post', 'timestamp']

    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.timestamp = timezone.now()  

        if commit:
            instance.save()

        return instance
