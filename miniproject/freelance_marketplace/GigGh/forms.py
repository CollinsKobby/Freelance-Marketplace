from django import forms
from .models import Gig, Bid, Submission, Chat
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class GigForm(forms.ModelForm):
    class Meta:
        model = Gig
        exclude = ['seller'] 
        fields = ['title', 'description', 'category', 'timeline_type',
                 'timeline_fixed_date', 'timeline_duration_start',
                 'timeline_duration_end', 'starting_price', 
                 'ending_price', 'image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Ensure timeline_type choices match model
        self.fields['timeline_type'].choices = Gig.TimelineType
        
        # Set required fields
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['timeline_type'].required = True
        
        # Set widget attributes
        self.fields['starting_price'].widget.attrs.update({
            'min': '0.01',
            'step': '0.01'
        })
        self.fields['ending_price'].widget.attrs.update({
            'min': '0.01',
            'step': '0.01'
        })

    def clean(self):
        cleaned_data = super().clean()
        timeline_type = cleaned_data.get('timeline_type')
        
        # Validate timeline fields
        if timeline_type == 'fixed_date' and not cleaned_data.get('timeline_fixed_date'):
            self.add_error('timeline_fixed_date', 'This field is required')
        elif timeline_type == 'duration':
            if not cleaned_data.get('timeline_duration_start'):
                self.add_error('timeline_duration_start', 'This field is required')
            if not cleaned_data.get('timeline_duration_end'):
                self.add_error('timeline_duration_end', 'This field is required')
        
        # Validate prices
        starting_price = cleaned_data.get('starting_price')
        ending_price = cleaned_data.get('ending_price')
        if starting_price and ending_price and ending_price < starting_price:
            self.add_error('ending_price', 'Must be greater than starting price')
        
        return cleaned_data
    
class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['biddingAmount', 'notes', 'attachment']  # Removed biddingCurrency
        widgets = {
            'biddingAmount': forms.NumberInput(attrs={
                'min': '0.01',
                'step': '0.01',
                'class': 'form-control',
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'attachment': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            })
        }

    def __init__(self, *args, **kwargs):
        self.gig = kwargs.pop('gig', None)
        self.freelancer = kwargs.pop('freelancer', None)
        super().__init__(*args, **kwargs)
        
        # Make fields optional
        self.fields['notes'].required = False
        self.fields['attachment'].required = False

    def save(self, commit=True):
        bid = super().save(commit=False)
        bid.gigId = self.gig
        bid.freelancer = self.freelancer
        bid.biddingCurrency = 'GHS'  # Set default currency
        
        if 'attachment' in self.cleaned_data and self.cleaned_data['attachment']:
            bid.attachment_name = self.cleaned_data['attachment'].name
        
        if commit:
            bid.save()
        return bid
        
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
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add your custom attributes
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })

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