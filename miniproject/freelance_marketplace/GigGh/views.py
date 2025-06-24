from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Gig, Bid, Submission, Chat, Payment
from .forms import GigForm, BidForm, SubmissionForm

#@login_required
def home(request):
    gigs = Gig.objects.filter(status='open').order_by('-created_at')
    return render(request, 'marketplace/home.html', {'gigs': gigs})

#@login_required
def create_gig(request):
    if request.method == 'POST':
        form = GigForm(request.POST, request.FILES)
        if form.is_valid():
            gig = form.save(commit=False)
            gig.seller = request.user
            gig.save()
            return redirect('gig_detail', gig_id=gig.id)
    else:
        form = GigForm()
    return render(request, 'marketplace/gig_form.html', {'form': form})

#@login_required
def gig_detail(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    bids = Bid.objects.filter(gig=gig).order_by('biddingAmount')
    accepted_bid = bids.filter(status='accepted').first()
    submission = Submission.objects.filter(bid=accepted_bid).first() if accepted_bid else None
    
    # Chat messages
    if request.user == gig.seller or request.user == accepted_bid.freelancer:
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