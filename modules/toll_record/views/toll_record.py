from django.views.generic import ListView
from modules.toll_record.models import TollRecord


class TollRecordListView(ListView):
    model = TollRecord
    template_name = 'toll_records/page-list.html'
    context_object_name = 'toll_records'

    def get_queryset(self):
        queryset = super().get_queryset()
        lince_plate = self.request.GET.get('lince_plate')
        if lince_plate:
            queryset = queryset.filter(lince_plate__icontains=lince_plate)
        else:
            queryset = queryset.none()
        return queryset
