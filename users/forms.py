from django import forms
from .models import User
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

from datetime import datetime


class SignInForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    
    def clean_password(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = User.objects.filter(email=email).first() # emails are unique

        if user:
            if check_password(password, user.password):
                return password
            else:
                raise forms.ValidationError("Incorrect password.")
        else:
            raise forms.ValidationError("No account associated with this email.")


class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}), 
        label='First Name'
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}), 
        label='Last Name'
    )
    email = forms.EmailField(
        max_length=30, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    date_of_birth = forms.CharField(
        widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Date of Birth', 
                'id': 'dob-selector'
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}), 
        label='Confirm password'
    )
    profile_photo = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Profile Photo', 
            "id": "profile-photo-field"}), 
        label='Profile Photo', 
        required=False
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'date_of_birth', 'password', 'password2', 'profile_photo')

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match.")
        return password2
    
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')

        if date_of_birth:
            # Parse the date string in "d-m-Y" format
            parsed_date = datetime.strptime(date_of_birth, "%d/%m/%Y")
            # Format the date into "Y-m-d" format
            formatted_date = parsed_date.strftime("%Y-%m-%d")
            return formatted_date


class UpdateUserForm(forms.ModelForm):
    first_name = forms.CharField(
        label='First Name'
    )
    last_name = forms.CharField(
        label='Last Name'
    )
    email = forms.EmailField(
        max_length=30, 
        label='Email Address'
    )
    # overriding the clear current
    profile_photo = forms.ImageField(
        widget=forms.FileInput,
        required=False,
    ) 
    # keeping the same date format
    date_of_birth = forms.DateField(
        widget=forms.DateInput(format=['&d/%m/%Y']),
        input_formats=settings.DATE_INPUT_FORMATS,
        label='Date of Birth'
    )

    class Meta():
        model = User
        exclude = ['id', 'is_active', 'is_admin', 'last_login', 'password', 'liked_posts', 'friends', 'friend_requests']
        input_formats = {'date_of_birth': ['%d/%m/%Y']}


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}), 
        label='Confirm password'
    )
