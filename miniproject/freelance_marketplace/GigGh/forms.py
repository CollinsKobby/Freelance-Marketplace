from django import forms
from .models import Gig, Bid, Submission, Chat
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

class GigForm(forms.ModelForm):
    class Meta:
        model = Gig
        fields = [
            'title',
            'description',
            'category',
            'starting_price',
            'ending_price',
            'currency',
            'timeline_type',
            'timeline_fixed_date',
            'timeline_duration_start',
            'timeline_duration_end',
            'image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'timeline_fixed_date': forms.DateInput(attrs={'type': 'date'}),
            'timeline_duration_start': forms.DateInput(attrs={'type': 'date'}),
            'timeline_duration_end': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        timeline_type = cleaned_data.get('timeline_type')
        timeline_fixed_date = cleaned_data.get('fixed_date')
        timeline_duration_start = cleaned_data.get('duration_start')
        timeline_duration_end = cleaned_data.get('duration_end')
        
        if timeline_type == 'fixed' and not timeline_fixed_date:
            self.add_error('fixed_date', 'Please select a fixed date')
        elif timeline_type == 'duration':
            if not timeline_duration_start or not timeline_duration_end:
                self.add_error('duration_start', 'Please select start and end dates')
            elif timeline_duration_start >= timeline_duration_end:
                self.add_error('duration_end', 'End date must be after start date')
        
        starting_price = cleaned_data.get('starting_price')
        ending_price = cleaned_data.get('ending_price')
        if ending_price and starting_price > ending_price:
            self.add_error('ending_price', 'Ending price must be higher than starting price')
        
        return cleaned_data

class BidForm(forms.ModelForm):
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = Bid
        fields = ['biddingAmount', 'notes', 'biddingCurrency']
        widgets = {
            'biddingAmount': forms.NumberInput(attrs={'min': 0}),
        }

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['submissionFile', 'submissionNotes']
        widgets = {
            'submissionNotes': forms.Textarea(attrs={'rows': 3}),
        }

class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['message']

User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username or Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class EditProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'}),
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )
    
    class Meta:
        model = User
        fields = [
            'profile_picture',
            'first_name',
            'last_name',
            'bio',
            'phone_number',
            'paymentmethod',
            'paymentmethodaccount'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }