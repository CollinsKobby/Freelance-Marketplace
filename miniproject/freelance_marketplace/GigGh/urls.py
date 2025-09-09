from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import login_View, signup, logout_view
from django.conf import settings  # For accessing MEDIA_URL and MEDIA_ROOT
from django.conf.urls.static import static  # For serving files during development

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('gigs/new/', views.create_gig, name='create_gig'),
    path('gigs/<int:gig_id>/', views.gig_detail, name='gig_detail'),
    path('gigs/<int:gig_id>/edit/', views.edit_gig, name='edit_gig'),
    path('gigs/<int:gig_id>/bid/', views.place_bid, name='place_bid'),
    path('bid/<int:bid_id>/', views.bid_detail, name='bid_detail'),
    path('bids/<int:bid_id>/accept/', views.accept_bid, name='accept_bid'),
    path('bid/<int:bid_id>/cancel/', views.cancel_bid, name='cancel_bid'),
    path('gigs/<int:gig_id>/submit/', views.submit_work, name='submit_work'),
    path('chat/<int:gig_id>/', views.chat_view, name='chat_view'),
    path('send_chat/<int:gig_id>/', views.send_chat, name='send_chat'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/signup/', views.signup_view, name='signup'),  
    path('accounts/logout/', views.logout_view, name='logout'),
    
    # Password reset URLs
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)