from django.contrib import admin
from .models import Reservation, Guest, Room, Service

admin.site.register(Reservation)
admin.site.register(Guest)
admin.site.register(Room)
admin.site.register(Service)

