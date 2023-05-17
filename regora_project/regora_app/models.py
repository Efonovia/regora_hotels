from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class GuestManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        username = self.model.normalize_username(username)
        guest = self.model(username=username, **extra_fields)
        guest.set_password(password)  # Use set_password to hash the password
        guest.save(using=self._db)
        return guest

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class Guest(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, default='default_username')
    first_name = models.CharField(max_length=20, null=False)
    last_name = models.CharField(max_length=20, null=False)
    email = models.EmailField(max_length=50, unique=True, null=False)
    date_created = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=11, null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'phone_number']

    objects = GuestManager()

    class Meta:
        verbose_name = 'Guest'
        verbose_name_plural = 'Guests'

    def __str__(self):
        return f'{self.username}'



class Room(models.Model):
    ROOM_CHOICES = [(i, f"Room{i}") for i in range(1, 52)]
    room_number = models.IntegerField(choices=ROOM_CHOICES, unique=True)
    is_available = models.BooleanField(default=True)

    def getType(self):
        if self.room_number <= 17:
            return "basic"
        elif 17 < self.room_number <= 34:
            return "premium"
        else:
            return "executive"

    def __str__(self):
        return f"Room{self.room_number} ({self.getType()})"


class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name



class Reservation(models.Model):
    guest= models.ForeignKey(Guest, null=True, on_delete= models.SET_NULL)
    room= models.ForeignKey(Room, null=True, on_delete= models.SET_NULL)
    services = models.ManyToManyField(Service)
    date_booked = models.DateTimeField(auto_now_add=True)
    begin_date = models.DateField()
    end_date = models.DateField()
    pickup_time = models.TimeField(default="None", max_length=20, null=True, blank=True)
    dropoff_time = models.TimeField(default="nothing", max_length=20, null=True, blank=True)
        
    def getCost(self):

        prices = {
            "basic": 20,
            "premium": 30,
            "executive": 50
        }

        return (self.end_date - self.begin_date) * prices[self.room.getType()]


    def __str__(self):
        room_number = self.room.room_number if self.room is not None else None
        guest_name = f"{self.guest.first_name} {self.guest.last_name}" if self.guest is not None else None
        duration = (self.end_date - self.begin_date).days if self.begin_date and self.end_date else None
        cost = self.getCost() if self.room is not None else None
        return f"Room{room_number} by {guest_name} for {duration} days at {cost} dollars"
        