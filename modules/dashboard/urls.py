from modules.authentication.urls import app_name
from django.urls import path
from modules.dashboard.views.dashboard import DashboardView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
]