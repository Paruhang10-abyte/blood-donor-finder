from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('toggle/', views.toggle, name='toggle'),
    path('search/', views.search, name='search'),
    path('request/<int:donor_id>/', views.submit_request, name='request'),
    path('request-sent/', views.request_sent, name='request_sent'),
    path('update-request/<int:request_id>/<str:status>/', views.update_request, name='update_request'),
    path('check-status/', views.check_status, name='check_status'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('cancel-request/<int:request_id>/', views.cancel_request, name='cancel_request'),
]
