from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Gig, Bid, Submission, Chat
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
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
    bids = Bid.objects.filter(freelancer=user).select_related('gig')
    
    context = {
        'user': user,
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
    submission = Submission.objects.filter(bid=accepted_bid).first() if accepted_bid else None
    
    # Chat messages
    if request.user == gig.seller or (accepted_bid and request.user == accepted_bid.freelancer):
        chat_messages = Chat.objects.filter(gig=gig).order_by('timestamp')
    else:
        chat_messages = None
    
    context = {
        'gig': gig,
        'bids': bids,
        'accepted_bid': accepted_bid,
        'submission': submission,
        'chat_messages': chat_messages,
    }
    return render(request, 'marketplace/gig_detail.html', context)

@login_required
def place_bid(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    
    if request.method == 'POST':
        form = BidForm(request.POST, gig=gig, freelancer=request.user)
        
        if form.is_valid():
            try:
                bid = form.save()
                messages.success(request, "Bid submitted successfully!")
                bid.save()
                return redirect('gig_detail', gig_id=gig.id)
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = BidForm()
    
    return render(request, 'marketplace/bid_form.html', {
        'form': form,
        'gig': gig
    })


@login_required
def bid_detail(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id)
    gig = bid.gigId
    
    # Only allow gig owner or bid creator to view
    if request.user != gig.seller and request.user != bid.freelancer:
        return HttpResponseForbidden("You don't have permission to view this bid")
    
    return render(request, 'marketplace/bid_detail.html', {
        'bid': bid,
        'gig': gig
    })


@login_required
def accept_bid(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id)
    
    # Permission check - only gig owner can accept bids
    if request.user != bid.gig.seller:
        messages.error(request, "You don't have permission to accept bids for this gig")
        return redirect('gig_detail', gig_id=bid.gig.id)
    
    # Only allow accepting bids for open gigs
    if bid.gig.status != 'open':
        messages.error(request, "Cannot accept bids for closed gigs")
        return redirect('gig_detail', gig_id=bid.gig.id)
    
    # Update all bids for this gig
    Bid.objects.filter(gig=bid.gig).update(status='rejected')
    bid.status = 'accepted'
    bid.save()
    
    # Close the gig after accepting a bid
    bid.gig.status = 'closed'
    bid.gig.save()
    
    messages.success(request, f"Bid from {bid.freelancer.username} accepted successfully!")
    return redirect('gig_detail', gig_id=bid.gig.id)


@login_required
def cancel_bid(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id)
    
    # Permission check - only bid creator or gig owner can cancel
    if request.user not in [bid.freelancer, bid.gig.seller]:
        messages.error(request, "You don't have permission to cancel this bid")
        return redirect('gig_detail', gig_id=bid.gig.id)
    
    # Only allow canceling pending bids
    if bid.status != 'pending':
        messages.error(request, "Only pending bids can be canceled")
        return redirect('gig_detail', gig_id=bid.gig.id)
    
    # If gig owner is canceling an accepted bid, reopen the gig
    if bid.status == 'accepted' and request.user == bid.gig.seller:
        bid.gig.status = 'open'
        bid.gig.save()
    
    bid.status = 'canceled'
    bid.save()
    
    actor = "You" if request.user == bid.freelancer else f"{bid.gig.seller.username}"
    messages.success(request, f"{actor} canceled the bid from {bid.freelancer.username}")
    return redirect('gig_detail', gig_id=bid.gig.id)



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

#@login_required
def send_chat(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.gig = gig
            message.sender = request.user
            message.recipient = gig.seller if request.user != gig.seller else message.bid.freelancer
            message.save()
            return redirect('gig_detail', gig_id=gig.id)
    return redirect('gig_detail', gig_id=gig.id)