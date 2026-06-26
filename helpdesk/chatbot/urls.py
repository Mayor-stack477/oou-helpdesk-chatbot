from django.urls import path
from . import views

urlpatterns = [

    # Home
    path('', views.home, name='home'),

    # Student Authentication
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Admin Authentication
    path("admin-login/", views.admin_login, name="admin_login"),

    # Admin Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),

    # Chatbot
    path('chat/', views.chatbot_response, name='chat'),
    path('chatbot_response/', views.chatbot_response, name='chatbot_response'),

    # Upload
    path('upload/', views.upload_file, name='upload_file'),

    # Rating
    path('rate-message/', views.rate_message, name='rate_message'),

    # Debug
    path('test_openai/', views.test_openai, name='test_openai'),
    path('test-ml/', views.test_ml_only, name='test_ml'),
    path('check_intent/', views.check_intent, name='check_intent'),
    path('health/', views.health_check, name='health'),

]