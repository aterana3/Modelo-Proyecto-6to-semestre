from django.http import JsonResponse
from django.views.generic import ListView
from modules.toll_record.models import TollRecord
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum


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


class AnalyticsView(LoginRequiredMixin, View):
    def get(self, request):
        total_revenue = TollRecord.objects.filter(paid=True).aggregate(Sum('amount_due'))['amount_due__sum'] or 0.00
        last_vehicle = TollRecord.objects.latest('pass_date').license_plate if TollRecord.objects.exists() else "N/A"

        start_date = timezone.now() - timedelta(days=5)
        vehicle_frequency = (
            TollRecord.objects.filter(pass_date__gte=start_date)
            .extra(select={'day': 'DATE(pass_date)'})
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        # Elimina el uso de `strftime` si `day` ya está en el formato correcto
        vehicle_frequency_data = {entry['day']: entry['count'] for entry in vehicle_frequency}

        daily_revenue = (
            TollRecord.objects.filter(pass_date__gte=start_date, paid=True)
            .extra(select={'day': 'DATE(pass_date)'})
            .values('day')
            .annotate(total=Sum('amount_due'))
            .order_by('day')
        )
        daily_revenue_data = {entry['day']: entry['total'] for entry in daily_revenue}

        data = {
            'total_revenue': total_revenue,
            'last_vehicle': last_vehicle,
            'vehicle_frequency': vehicle_frequency_data,
            'daily_revenue': daily_revenue_data,
        }
        return JsonResponse(data)
