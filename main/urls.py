from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:user_id>/', views.public_profile, name='public_profile'),

    path('request/', views.create_request, name='request'),
    path('register/', views.register, name='register'),
    path('available-requests/', views.available_requests, name="available_requests"),

    path('requests/', views.show_requests, name='requests'),
    path('requests/<int:pk>/toggle-save/', views.toggle_save_request, name='toggle-save-request'),
    path('requests/<int:pk>/update/', views.update_request, name='update_request'),
    path('requests/<int:pk>/delete/', views.delete_request, name='delete_request'),
    path('requests/<int:pk>/details/', views.request_details, name='request_details'),

    path("login/", auth_views.LoginView.as_view(template_name="webui/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
]

