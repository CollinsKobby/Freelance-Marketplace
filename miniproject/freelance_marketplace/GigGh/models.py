from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class User(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=254)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=100)
    paymentmethod = models.CharField(max_length=50, blank=True, null=True)
    paymentmethodaccount = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.email


class Gig(models.Model):
    class TimelineType(models.TextChoices):
        FIXED_DATE = 'FIXED_DATE', 'Fixed Date'
        DURATION = 'DURATION', 'Duration'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    ending_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    timeline_type = models.CharField(
        max_length=20,
        choices=TimelineType.choices
    )
    timeline_fixed_date = models.DateField(blank=True, null=True)
    timeline_duration_start = models.DateField(blank=True, null=True)
    timeline_duration_end = models.DateField(blank=True, null=True)
    image = models.TextField()  # base64 string
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN
    )

    def __str__(self):
        return self.title
    

class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    gigId = models.ForeignKey('Gig', on_delete=models.CASCADE, related_name='bids')
    biddingAmount = models.DecimalField(max_digits=10, decimal_places=2)
    biddingCurrency = models.CharField(max_length=10)
    
    STATUS_CHOICES = [
        ('opened', 'Opened'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='opened')

    def __str__(self):
        return f"Bid {self.id} - {self.biddingAmount} {self.biddingCurrency} ({self.status})"
    



class Submission(models.Model):
    id = models.AutoField(primary_key=True)
    gigId = models.ForeignKey('Gig', on_delete=models.CASCADE, related_name='submissions')
    bidId = models.ForeignKey('Bid', on_delete=models.CASCADE, related_name='submissions')
    submissionFile = models.TextField()  # base64-encoded file content
    submissionNotes = models.TextField(blank=True)

    def __str__(self):
        return f"Submission {self.id} for Gig {self.gigId_id} via Bid {self.bidId_id}"
    



class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.AutoField(primary_key=True)
    submissionId = models.ForeignKey('Submission', on_delete=models.CASCADE, related_name='payments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payer = models.ForeignKey('User', on_delete=models.CASCADE, related_name='payments_made')
    payee = models.ForeignKey('User', on_delete=models.CASCADE, related_name='payments_received')

    def __str__(self):
        return f"Payment {self.id} - {self.status}"





class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey('User', on_delete=models.CASCADE, related_name='chats_sent')
    recipient = models.ForeignKey('User', on_delete=models.CASCADE, related_name='chats_received')
    message = models.TextField()
    room = models.CharField(max_length=100)

    def __str__(self):
        return f"Chat from {self.sender_id} to {self.recipient_id} in {self.room}"