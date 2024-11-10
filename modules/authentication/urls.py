from django.urls import path
from modules.authentication.views.authentication import LoginView, LogoutView

app_name = 'authentication'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView, name='logout'),
]