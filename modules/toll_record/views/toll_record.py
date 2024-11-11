from django.views.generic import ListView
from modules.toll_record.models import TollRecord


class TollRecordListView(ListView):
    model = TollRecord
    template_name = 'toll_records/page-list.html'
    context_object_name = 'toll_records'

    def get_queryset(self):
        queryset = super().get_queryset()
        license_plate = self.request.GET.get('license_plate')
        if license_plate:
            queryset = queryset.filter(license_plate__icontains=license_plate)
        else:
            queryset = queryset.none()
        return queryset
