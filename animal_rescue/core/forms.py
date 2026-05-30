from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    AdoptionRequest, RescueRequest, LostFoundReport, 
    Appointment, ChatMessage, Donation, UserProfile
)

# ============ AUTHENTICATION FORMS ============
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[('User', 'Regular User'), ('Volunteer', 'Volunteer')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'
    }))
    address = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 3,
        'placeholder': 'Your Address'
    }))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'address', 'role', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

# ============ ADOPTION REQUEST FORM ============
class AdoptionForm(forms.ModelForm):
    class Meta:
        model = AdoptionRequest
        fields = ['name', 'phone', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Tell us about yourself and why you want to adopt this cat...'}),
        }

# ============ RESCUE REQUEST FORM ============
class RescueRequestForm(forms.ModelForm):
    class Meta:
        model = RescueRequest
        fields = ['title', 'description', 'location', 'latitude', 'longitude', 'urgency_reason', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief title (e.g., Injured cat on Main Street)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detailed description of the situation...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Exact location or address'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Latitude (optional)'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Longitude (optional)'}),
            'urgency_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Why is this urgent? (injuries, weather, etc.)'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

# ============ LOST & FOUND FORM ============
class LostFoundForm(forms.ModelForm):
    class Meta:
        model = LostFoundReport
        fields = ['report_type', 'cat_name', 'cat_description', 'breed', 'color', 'location', 'latitude', 'longitude', 'image', 'contact_phone', 'contact_email']
        widgets = {
            'report_type': forms.Select(attrs={'class': 'form-select'}),
            'cat_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cat name (if known)'}),
            'cat_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed description...'}),
            'breed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Breed (optional)'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cat color/markings'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last seen location or found at'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Latitude (optional)'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Longitude (optional)'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your phone number'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email'}),
        }

# ============ APPOINTMENT FORM ============
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['scheduled_date', 'notes']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special notes or questions?'
            }),
        }

# ============ CHAT MESSAGE FORM ============
class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Type your message here...'
            }),
        }

# ============ DONATION FORM ============
class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['donor_name', 'donor_email', 'amount', 'donation_type', 'message', 'is_anonymous']
        widgets = {
            'donor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'donor_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount (PKR)', 'step': '0.01'}),
            'donation_type': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional message...'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# ============ USER PROFILE FORM ============
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'latitude', 'longitude', 'bio', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }