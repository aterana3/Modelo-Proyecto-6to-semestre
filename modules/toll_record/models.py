from django.db import models
from modules.core.models import ModelBase, Location


# Create your models here.
class TollRecord(ModelBase):
    lince_plate = models.CharField(max_length=20, verbose_name="License Plate")
    pass_date = models.DateTimeField(verbose_name="Pass Date")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="Location")
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount Due")
    paid = models.BooleanField(default=False, verbose_name="Paid")
    image = models.ImageField(upload_to='toll_records', verbose_name="Image")

    def __str__(self):
        return '{}'.format(self.lince_plate)

    class Meta:
        verbose_name = 'Toll Record'
        verbose_name_plural = 'Toll Records'
        db_table = 'toll_records'
