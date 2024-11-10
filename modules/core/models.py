from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class ModelBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    avatar = models.ImageField(verbose_name='Avatar', upload_to='avatars', null=True, blank=True)
    email = models.EmailField(verbose_name='Email', unique=True)
    phone = models.CharField(verbose_name='Phone', max_length=15, null=True, blank=True)
    direction = models.CharField(verbose_name='Direction', max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return '{}'.format(self.username)

    @property
    def created_at_format(self):
        return self.created_at.strftime('%d/%m/%Y %H:%M:%S')

    @property
    def updated_at_format(self):
        return self.updated_at.strftime('%d/%m/%Y %H:%M:%S')

    @property
    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.webp'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'users'
