from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from freelance_marketplace import settings
from django.conf import settings
from django.contrib.auth import get_user_model

# Create your models here.

class User(AbstractUser):
    PAYMENT_METHODS = [
        ('mobile_money', 'Mobile Money'),
        ('bank', 'Bank Transfer')
    ]

    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=254)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=100)
    paymentmethod = models.CharField(max_length=20, choices=PAYMENT_METHODS, blank=True)
    paymentmethodaccount = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )
    phone_number = models.CharField(max_length=20, blank=True)
    
    def save(self, *args, **kwargs):
        # Delete old profile picture when updating
        try:
            old = User.objects.get(id=self.id)
            if old.profile_picture != self.profile_picture:
                old.profile_picture.delete(save=False)
        except:
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class Gig(models.Model):
    class TimelineType(models.TextChoices):
        FIXED_DATE = 'fixed_date', 'Fixed Date'
        DURATION = 'duration', 'Duration'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'

    class Category(models.TextChoices):
        DESIGN = 'design', 'Design'
        DEVELOPMENT = 'development', 'Development'
        WRITING = 'writing', 'Writing'
        ADMINISTRATIVE = 'administrative', 'Administrative'

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gigs')
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        max_length=15,
        choices=Category.choices,
        default=Category.DEVELOPMENT
    )
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    ending_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='GHS')
    timeline_type = models.CharField(
        max_length=20,
        choices=TimelineType.choices
    )
    timeline_fixed_date = models.DateField(blank=True, null=True)
    timeline_duration_start = models.DateField(blank=True, null=True)
    timeline_duration_end = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to='gig_images/', blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    gigId = models.ForeignKey('Gig', on_delete=models.PROTECT, related_name='bids')
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bids'
    )
    biddingAmount = models.DecimalField(max_digits=10, decimal_places=2)
    biddingCurrency = models.CharField(max_length=10, default='GHS')
    notes = models.TextField(blank=True, null=True)
    attachment = models.FileField(
        upload_to='bid_attachments/',
        null=True,
        blank=True,
        verbose_name='Attachment'
    )
    attachment_name = models.CharField(max_length=255, blank=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid {self.id} - {self.biddingAmount} {self.biddingCurrency} ({self.status})"
    



class Submission(models.Model):
    id = models.AutoField(primary_key=True)
    gigId = models.ForeignKey('Gig', on_delete=models.CASCADE, related_name='submissions')
    bidId = models.ForeignKey('Bid', on_delete=models.CASCADE, related_name='submissions')
    submissionFile = models.FileField(upload_to='submissions/')
    submissionNotes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

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



User = get_user_model()

class Chat(models.Model):
    gig = models.ForeignKey('Gig', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender} to {self.recipient}: {self.message[:20]}..."