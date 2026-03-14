from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from .models import Slot, Booking
from .forms import SlotForm
from accounts.models import User
from .google_calendar import create_calendar_event
import requests
import os


@login_required
def dashboard(request):
    user = request.user
    if user.is_doctor():
        slots = Slot.objects.filter(doctor=user).order_by('date', 'start_time')
        bookings = Booking.objects.filter(slot__doctor=user).select_related('patient', 'slot')
        return render(request, 'appointments/doctor_dashboard.html', {
            'slots': slots,
            'bookings': bookings,
        })
    else:
        today = timezone.now().date()
        available_slots = Slot.objects.filter(
            is_booked=False,
            date__gte=today
        ).select_related('doctor').order_by('date', 'start_time')
        my_bookings = Booking.objects.filter(patient=user).select_related('slot__doctor')
        return render(request, 'appointments/patient_dashboard.html', {
            'available_slots': available_slots,
            'my_bookings': my_bookings,
        })


@login_required
def add_slot(request):
    if not request.user.is_doctor():
        messages.error(request, 'Only doctors can add availability slots.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = SlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.doctor = request.user
            slot.save()
            messages.success(request, 'Availability slot added successfully!')
            return redirect('dashboard')
    else:
        form = SlotForm()
    return render(request, 'appointments/add_slot.html', {'form': form})


@login_required
def delete_slot(request, slot_id):
    if not request.user.is_doctor():
        return redirect('dashboard')
    slot = get_object_or_404(Slot, id=slot_id, doctor=request.user)
    if not slot.is_booked:
        slot.delete()
        messages.success(request, 'Slot deleted.')
    else:
        messages.error(request, 'Cannot delete a slot that is already booked.')
    return redirect('dashboard')


@login_required
def book_slot(request, slot_id):
    if not request.user.is_patient():
        messages.error(request, 'Only patients can book slots.')
        return redirect('dashboard')

    slot = get_object_or_404(Slot, id=slot_id, is_booked=False)

    if request.method == 'POST':
        with transaction.atomic():
            # Lock the row to prevent race conditions
            slot = Slot.objects.select_for_update().get(id=slot_id)
            if slot.is_booked:
                messages.error(request, 'Sorry, this slot was just booked by someone else.')
                return redirect('dashboard')

            booking = Booking.objects.create(slot=slot, patient=request.user)
            slot.is_booked = True
            slot.save()

        # Send confirmation email via serverless function
        try:
            requests.post(
                os.getenv('SERVERLESS_EMAIL_URL', 'http://localhost:3000/dev/send-email'),
                json={
                    'action': 'BOOKING_CONFIRMATION',
                    'patient_email': request.user.email,
                    'doctor_email': slot.doctor.email,
                    'patient_name': request.user.username,
                    'doctor_name': slot.doctor.username,
                    'date': str(slot.date),
                    'start_time': str(slot.start_time),
                    'end_time': str(slot.end_time),
                },
                timeout=5
            )
        except Exception:
            pass  # Don't fail booking if email service is down

        # Create Google Calendar event
        try:
            create_calendar_event(slot, request.user, slot.doctor)
        except Exception as e:
            # Log but don't block the booking
            print(f"Google Calendar error: {e}")

        messages.success(request, f'Appointment booked with Dr. {slot.doctor.username}!')
        return redirect('dashboard')

    return render(request, 'appointments/book_slot.html', {'slot': slot})
