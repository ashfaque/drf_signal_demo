from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView 
from . import views

urlpatterns = [
    path('create/', views.ListCreateUserView.as_view(), name = 'create_user_view'),
    path('login/', views.LoginUserView.as_view(), name = 'login_user_view'),
    path('login/refresh/', TokenRefreshView.as_view(), name = 'login_refresh_user_view'),
    path('logout/', views.LogoutUserView.as_view(), name = 'logout_user_view'),
    path('password/change/', views.ChangePasswordView.as_view(), name = 'change_password_view'),
    path('password/forgot/', views.ForgotPasswordView.as_view(), name = 'forgot_password_view'),

]