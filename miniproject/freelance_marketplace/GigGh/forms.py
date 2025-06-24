from django import forms
from .models import Gig, Bid, Submission

class GigForm(forms.ModelForm):
    class Meta:
        model = Gig
        fields = ['title', 'description', 'starting_price', 'ending_price', 
                 'currency', 'timeline_type', 'timeline_fixed_date', 'timeline_duration_start', 
                 'timeline_duration_end', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'timeline_fixed_date': forms.DateInput(attrs={'type': 'date'}),
            'timeline_duration_start': forms.DateInput(attrs={'type': 'date'}),
            'timeline_duration_end': forms.DateInput(attrs={'type': 'date'}),
        }

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['biddingAmount', 'biddingCurrency']
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