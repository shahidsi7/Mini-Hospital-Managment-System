from django.contrib import admin
from .models import Slot, Booking


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('is_booked', 'date', 'doctor')
    search_fields = ('doctor__username',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'slot', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('patient__username', 'slot__doctor__username')
