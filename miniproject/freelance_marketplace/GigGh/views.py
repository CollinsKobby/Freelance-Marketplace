from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Gig, Bid, Submission, Chat
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import GigForm, BidForm, SubmissionForm, ChatForm, LoginForm, SignupForm, EditProfileForm
from django.views import View
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden

#class CustomLoginView(LoginView):
#    form_class = LoginForm
#    template_name = 'registration/login.html'

def signup(request):
    if request.method == 'POST':
        print("Form submitted!")  # Debug
        form = SignupForm(request.POST)
        print("Form errors:", form.errors)  # Debug
        if form.is_valid():
            print("Form is valid!")  # Debug
            user = form.save()
            print("User created:", user.username)  # Debug
            login(request, user)
            return redirect('home')
        else:
            print("Form invalid:", form.errors)  # Debug
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_View(request):
    error_message = None

    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'home'
            return redirect(next_url)
        else:
            error_message = "Invalid Credentials"
    return render(request, 'registration/login.html', {'error' : error_message})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    else:
        return redirect('home')

#@login_required
def home(request):
    gigs = Gig.objects.filter(status='open').order_by('-created_at')[:12]
    context = {
        'gigs': gigs
    }
    return render(request, 'marketplace/home.html', context)

#@login_required
def profile(request):
    user = request.user
    posted_gigs = Gig.objects.filter(seller=user).order_by('-created_at')
    bids = Bid.objects.filter(freelancer=user).select_related('gigId').filter(gigId__isnull=False).order_by('-created_at')
    recent_gigs = request.user.gigs.order_by('-created_at')[:5]
    recent_bids = request.user.bids.select_related('gigId').order_by('-created_at')[:5]
    
    # Combine and sort activities
    activities = []
    
    for gig in recent_gigs:
        activities.append({
            'type': 'gig',
            'title': gig.title,
            'gig_id': gig.id,
            'timestamp': gig.created_at,
            'status': None
        })
    
    for bid in recent_bids:
        activities.append({
            'type': 'bid',
            'amount': bid.biddingAmount,
            'currency': bid.biddingCurrency,
            'gig_id': bid.gigId.id,
            'gig_title': bid.gigId.title,
            'timestamp': bid.created_at,
            'status': bid.status
        })
    
    # Sort combined activities by timestamp
    recent_activities = sorted(activities, key=lambda x: x['timestamp'], reverse=True)[:10]
    
    context = {
        'user': user,
        'recent_activities': recent_activities,
        'posted_gigs': posted_gigs,
        'bids': bids,
        'active_tab': request.GET.get('tab', 'overview')
    }
    return render(request, 'marketplace/profile.html', context)

#@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'marketplace/edit_profile.html', {
        'form': form,
        'active_tab': 'settings'
    })

@login_required
def create_gig(request):
    if request.method == 'POST':
        form = GigForm(request.POST, request.FILES)
        if form.is_valid():
            gig = form.save(commit=False)
            gig.seller_id = request.user.id
            gig.save()
            messages.success(request, "Gig created successfully!")
            return redirect('gig_detail', gig_id=gig.id)
        else:
            print("Form errors:", form.errors)
    else:
        form = GigForm()
    
    return render(request, 'marketplace/gig_form.html', {
        'form': form,
        'creating_new': True,
        'title': 'Create New Gig'
    })


@login_required
def edit_gig(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id, seller=request.user)
    
    if request.method == 'POST':
        form = GigForm(request.POST, request.FILES, instance=gig)
        if form.is_valid():
            updated_gig = form.save()
            messages.success(request, 'Gig updated successfully!')
            return redirect('gig_detail', gig_id=updated_gig.id)
    else:
        form = GigForm(instance=gig)
    
    context = {
        'form': form,
        'gig': gig,
        'creating_new': False,  # This tells template it's an edit form
        'title': f'Edit {gig.title}'
    }
    return render(request, 'marketplace/gig_form.html', context)

#@login_required
def gig_detail(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    bids = Bid.objects.filter(gigId=gig).order_by('biddingAmount')
    accepted_bid = bids.filter(status='accepted').first()
    submission = Submission.objects.filter(bidId=accepted_bid).first() if accepted_bid else None
    
    # Initialize chat variables
    show_chat = False
    chat_messages = []
    recipient = None

    if request.user.is_authenticated:
        # Determine if chat should be shown
        show_chat = (request.user == gig.seller or 
                    (accepted_bid and request.user == accepted_bid.freelancer))
        
        # Get chat messages if authorized
        if show_chat:
            recipient = gig.seller if request.user != gig.seller else accepted_bid.freelancer
            
            if recipient:  # Only proceed if we have a valid recipient
                chat_messages = Chat.objects.filter(
                    gig=gig
                ).filter(
                    Q(sender=request.user, recipient=recipient) |
                    Q(sender=recipient, recipient=request.user)
                ).order_by('timestamp')

    context = {
        'gig': gig,
        'bids': bids,
        'accepted_bid': accepted_bid,
        'submission': submission,
        'show_chat': show_chat,
        'chat_messages': chat_messages,
        'recipient': recipient,
        'current_user': request.user.username
    }
    return render(request, 'marketplace/gig_detail.html', context)

@login_required
def place_bid(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    
    if Bid.objects.filter(gigId=gig, freelancer=request.user).exists():
        messages.error(request, "You've already placed a bid on this gig")
        return redirect('gig_detail', gig_id=gig.id)
    
    if request.method == 'POST':
        form = BidForm(request.POST, request.FILES, gig=gig, freelancer=request.user)
        
        if form.is_valid():
            try:
                bid = form.save()
                messages.success(request, "Bid submitted successfully!")
                return redirect('gig_detail', gig_id=gig.id)
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = BidForm(gig=gig, freelancer=request.user)
    
    return render(request, 'marketplace/bid_form.html', {
        'form': form,
        'gig': gig
    })


@login_required
def bid_detail(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id)
    gig = bid.gigId  # Using gigId as per your model
    
    # Only allow gig owner or bid creator to view
    if request.user != gig.seller and request.user != bid.freelancer:
        return HttpResponseForbidden("You don't have permission to view this bid")
    
    # Get submission if exists (using bidId as per your model)
    submission = None
    if hasattr(bid, 'submission'):  # Check if submission exists
        submission = bid.submission
    elif hasattr(bid, 'submissions'):  # Check if reverse relation exists
        submission = bid.submissions.first()
    
    return render(request, 'marketplace/bid_detail.html', {
        'bid': bid,
        'gig': gig,
        'submission': submission
    })


@login_required
def accept_bid(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id)
    
    # Permission check - only gig owner can accept bids
    if request.user != bid.gigId.seller:  # Changed to gigId
        messages.error(request, "Only the gig owner can accept bids")
        return redirect('gig_detail', gig_id=bid.gigId.id)
    
    # Only allow accepting bids for open gigs
    if bid.gigId.status != 'open':  # Changed to gigId
        messages.error(request, "Cannot accept bids for closed gigs")
        return redirect('gig_detail', gig_id=bid.gigId.id)
    
    # Update all bids for this gig using gigId instead of gig
    Bid.objects.filter(gigId=bid.gigId).update(status='rejected')  # Fixed here
    bid.status = 'accepted'
    bid.save()
    
    # Close the gig after accepting a bid
    bid.gigId.status = 'closed'  # Changed to gigId
    bid.gigId.save()
    
    messages.success(request, f"Bid from {bid.freelancer.username} accepted successfully!")
    return redirect('gig_detail', gig_id=bid.gigId.id)  # Changed to gigId.id

@login_required
def cancel_bid(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id)
    gig = bid.gigId  # Store gig reference before deletion
    
    # Permission check
    if request.user not in [bid.freelancer, gig.seller]:
        messages.error(request, "You don't have permission to cancel this bid")
        return redirect('home')
    
    # Only allow canceling pending bids
    if bid.status != 'pending':
        messages.error(request, "Only pending bids can be canceled")
        return redirect('gig_detail', gig_id=gig.id)
    
    # Handle gig status if needed
    if bid.status == 'accepted' and request.user == gig.seller:
        gig.status = 'open'
        gig.save()
    
    # Delete the bid
    bid.delete()
    
    # Success message
    actor = "You" if request.user == bid.freelancer else gig.seller.username
    messages.success(request, f"Bid successfully canceled by {actor}")
    return redirect('gig_detail', gig_id=gig.id)  # Use .id here



#@login_required
def submit_work(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    accepted_bid = Bid.objects.filter(gig=gig, freelancer=request.user, status='accepted').first()
    
    if not accepted_bid:
        return redirect('home')
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.gig = gig
            submission.bid = accepted_bid
            submission.save()
            return redirect('gig_detail', gig_id=gig.id)
    else:
        form = SubmissionForm()
    
    return render(request, 'marketplace/submission_form.html', {'form': form, 'gig': gig})

@login_required
def chat_view(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    
    # Check if user is either the gig seller or has an accepted bid
    accepted_bid = Bid.objects.filter(
        gigId=gig, 
        freelancer=request.user, 
        status='accepted'
    ).first()
    
    if not (request.user == gig.seller or accepted_bid):
        raise PermissionDenied("You don't have permission to access this chat.")
    
    # Determine the other participant
    if request.user == gig.seller:
        recipient = accepted_bid.freelancer if accepted_bid else None
    else:
        recipient = gig.seller
    
    if not recipient:
        raise PermissionDenied("No chat available for this gig yet.")
    
    # Get chat messages
    chat_messages = Chat.objects.filter(
    Q(gig=gig, sender=request.user, recipient=recipient) |
    Q(gig=gig, sender=recipient, recipient=request.user)
)  # <-- This closing parenthesis was missing

    return render(request, 'partials/_chat.html', {
        'chat_messages': chat_messages,
        'recipient': recipient,
        'gig': gig,
        'bid': accepted_bid
    })

@login_required
def send_chat(request, gig_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        gig = get_object_or_404(Gig, id=gig_id)
        accepted_bid = Bid.objects.filter(
            gigId=gig, 
            freelancer=request.user, 
            status='accepted'
        ).first()
        
        # Verify chat participants
        if not (request.user == gig.seller or accepted_bid):
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Determine recipient
        recipient = gig.seller if request.user != gig.seller else accepted_bid.freelancer
        
        form = ChatForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.gig = gig
            message.bid = accepted_bid if accepted_bid else None
            message.sender = request.user
            message.recipient = recipient
            message.save()
            
            # Mark previous unread messages as read
            Chat.objects.filter(
                gig=gig,
                sender=recipient,
                recipient=request.user,
                is_read=False
            ).update(is_read=True)
            
            channel_layer = get_channel_layer()

            # Send via WebSocket
            async_to_sync(channel_layer.group_send)(
                f'chat_{gig_id}',
                {
                    'type': 'chat_message',
                    'message': message.message,
                    'sender': request.user.username,
                    'timestamp': message.timestamp.strftime('%H:%M'),
                    'sender_id': request.user.id
                }
            )
            
            return JsonResponse({
                'status': 'success',
                'message': message.message,
                'timestamp': message.timestamp.strftime('%H:%M'),
                'sender': request.user.username
            })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)