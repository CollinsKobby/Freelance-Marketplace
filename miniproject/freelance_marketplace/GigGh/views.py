from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Gig, Bid, Submission, Chat
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from .forms import GigForm, BidForm, SubmissionForm, ChatForm, LoginForm, SignupForm, EditProfileForm

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})

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

#login_required
def create_gig(request):
    if request.method == 'POST':
        form = GigForm(request.POST, request.FILES)
        if form.is_valid():
            gig = form.save(commit=False)
            gig.seller = request.user
            gig.save()
            messages.success(request, "Gig created successfully!")
            return redirect('gig_detail', gig_id=gig.id)
    else:
        form = GigForm()
    return render(request, 'marketplace/gig_form.html', {'form': form})

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

#@login_required
def place_bid(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.gig = gig
            bid.freelancer = request.user
            bid.save()
            return redirect('gig_detail', gig_id=gig.id)
    else:
        form = BidForm()
    return render(request, 'marketplace/bid_form.html', {'form': form, 'gig': gig})

#@login_required
def accept_bid(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id)
    if request.user != bid.gig.seller:
        return redirect('home')
    
    # Update all bids for this gig
    Bid.objects.filter(gig=bid.gig).update(status='rejected')
    bid.status = 'accepted'
    bid.save()
    
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