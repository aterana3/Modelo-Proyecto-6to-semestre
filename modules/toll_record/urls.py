from django.urls import path
from modules.authentication.urls import app_name
from modules.toll_record.views.toll_record import TollRecordListView, AnalyticsView

app_name = 'toll_record'

urlpatterns = [
    path('', TollRecordListView.as_view(), name='toll_record_list'),
    path('api/analytics/', AnalyticsView.as_view(), name='toll_record_analytics'),
]