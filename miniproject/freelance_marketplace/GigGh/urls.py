from django.urls import path
from . import views
from django.conf import settings  # For accessing MEDIA_URL and MEDIA_ROOT
from django.conf.urls.static import static  # For serving files during development

urlpatterns = [
    path('', views.home, name='home'),
    path('gigs/new/', views.create_gig, name='create_gig'),
    path('gigs/<int:gig_id>/', views.gig_detail, name='gig_detail'),
    path('gigs/<int:gig_id>/bid/', views.place_bid, name='place_bid'),
    path('bids/<int:bid_id>/accept/', views.accept_bid, name='accept_bid'),
    path('gigs/<int:gig_id>/submit/', views.submit_work, name='submit_work'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)