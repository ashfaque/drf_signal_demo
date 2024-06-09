from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView 
from . import views

urlpatterns = [
    path('create/', views.ListCreateUserView.as_view(), name = 'create_user_view'),    # POST: {"username":"TestUser3","first_name":"Test","last_name":"User","email":"testuser@example.com","user_type":"student","gender":"Male","phone_no":"123456789"}
    path('login/', views.LoginUserView.as_view(), name = 'login_user_view'),
    path('login/refresh/', TokenRefreshView.as_view(), name = 'login_refresh_user_view'),
    path('logout/', views.LogoutUserView.as_view(), name = 'logout_user_view'),    # Use POST with Body, {"refresh_token": "token here"}
    path('password/change/', views.ChangePasswordView.as_view(), name = 'change_password_view'),
    path('password/forgot/', views.ForgotPasswordView.as_view(), name = 'forgot_password_view'),
    path('celery_bg_task_test/', views.CeleryBgTaskTestView.as_view(), name = 'celery_bg_task_test_view'),

]