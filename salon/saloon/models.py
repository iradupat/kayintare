from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import datetime
from django.utils import  timezone


def array_summer(arr):
    sum = 0
    for el in arr:
        sum = sum + el.rate
    return sum


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    date_of_birth = models.DateField(default=timezone.now())
    phone = models.CharField(default='0789123090', max_length=20)
    gender = models.CharField(default="U", max_length=2)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()


class ManagerAccount(models.Model):
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)


class ClientAccount(models.Model):
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=False)


class Saloon(models.Model):
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=False)
    address = models.CharField(null=True, max_length=100)
    opening_hours = models.TimeField(verbose_name="Opening Hours")
    closing_hours = models.TimeField(verbose_name="Closing hours")
    saloon_name = models.CharField(max_length=40, blank=True)
    approved = models.BooleanField(default=False)

    def get_rate(self):
        ratings = Rating.objects.filter(saloon=self)
        print(ratings)
        if ratings.exists():
            all_rates = array_summer(ratings)
            return str(all_rates/len(ratings))+"/5"
        else:
            return "No ratings"


class SaloonService(models.Model):
    name = models.CharField(max_length=100, null=False)
    price = models.IntegerField(default=0)
    saloon = models.ForeignKey(Saloon, null=False, on_delete=models.CASCADE)


class Style(models.Model):
    name = models.CharField(max_length=100, null=False)
    service = models.ForeignKey(SaloonService, on_delete=models.CASCADE, null=False)


class File(models.Model):
    url = models.CharField(max_length=1000, null=False)
    name = models.CharField(max_length=40, null=True)
    style = models.ForeignKey(Style, on_delete=models.CASCADE, null=False)


RATES = [
    (1, 'one'),
    (2, 'two'),
    (3, 'three'),
    (4, 'four'),
    (5, 'five')
]


class Rating(models.Model):
    rate = models.IntegerField(choices=RATES)
    review = models.CharField(null=True, max_length=200)
    saloon = models.ForeignKey(Saloon, on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)


class Notification(models.Model):
    origin = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="origins")
    message = models.CharField(max_length=200)
    destination = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="destinations")
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)


REPORT_TYPE = [
    (1, 'BAD SERVICE'),
    (2, 'VERY EXPENSIVE')
]


class Report(models.Model):
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE)
    message = models.CharField(max_length=100, default='')
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE, null=True)


class Appointment(models.Model):
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE)
    client = models.ForeignKey(ClientAccount, on_delete=models.CASCADE)
    style = models.ForeignKey(Style, on_delete=models.SET_NULL, null=True)
    time = models.DateTimeField()
    approved = models.BooleanField(default=False)
    comment = models.CharField(max_length=200, default="")



