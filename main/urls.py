from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Auth
    path('register/', views.register,    name='register'),
    path('login/',    views.login_view,  name='login'),
    path('logout/',   views.logout_view, name='logout'),

    # Browse and Detail
    path('Search/',          views.Search,        name='Search'),
    path('hostel/<int:pk>/', views.hostel_detail, name='hostel_detail'),
    path('hostel/<int:pk>/save/', views.toggle_save, name='toggle_save'),

    # Dashboards
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('agent/dashboard/',   views.agent_dashboard,   name='agent_dashboard'),

    # Submit listing
    path('submit/', views.submit_listing, name='submit_listing'),
]