from datetime import datetime, time, timedelta
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .forms import ReservationForm, SignupForm
from django.contrib.auth import login, authenticate
from django.core.serializers import serialize
from django.utils import timezone


def home(request):
    return render(request, "home.html")


def signup(request):
    return render(request, "signup.html")


def createUser(request):
    form = SignupForm()  # Create an instance of the SignupForm

    if request.method == 'POST':
        form = SignupForm(request.POST)  # Bind form data to the request POST data

        if form.is_valid():
            email = form.cleaned_data['email']

            if Guest.objects.filter(email=email).exists():
                form.add_error('email', 'This email is already registered.')
            else:
                # Process the valid form data and create the guest object
                guest = Guest.objects.create(
                    username=email,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=email,
                    password=form.cleaned_data['password'],
                    phone_number=form.cleaned_data['phone_number']
                )

                # Redirect to the roomspage page with the guest ID as a URL parameter
                return redirect(f'/dashboard/?guest_id={guest.id}')

    return render(request, 'signup.html', {'form': form})


def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')

        print(username, password)
        try:
            guest = Guest.objects.get(username=username)
            print(f'retrieved guest: {guest}')
        except Guest.DoesNotExist:
            return render(request, 'login.html', {'error_message': 'Invalid username or password.'})

        print(guest.password)
        if guest.password == password and not guest.is_staff:
            # Log the user in
            login(request, guest)
            return redirect(f'/dashboard/?guest_id={guest.id}')
        else:
            # Authentication failed
            print("Authentication failed")
            return render(request, 'login.html', {'error_message': 'Invalid username or password.'})
    else:
        return render(request, 'login.html')


def roomspage(request):
    guest_id = request.GET.get('guest_id')
    if guest_id:
        guest = Guest.objects.get(id=guest_id)
    else:
        guest = None

    rooms = Room.objects.all()
    return render(request, 'roomspage.html', {'guest': guest, 'rooms': rooms})


def reservation(request):
    room_number = request.GET.get('room_number')
    guest_id = request.GET.get('guest_id')
    all_services = Service.objects.all()
    all_services_json = serialize('json', all_services)  # Serialize QuerySet to JSON
    all_services_data = json.loads(all_services_json)
    processed_all_services = json.dumps(all_services_data)

    room = Room.objects.get(room_number = room_number)
    if room.is_available:
        # print("000000000000000000000000000000000000000000000000000000000000000000000", target_reservation)
        return render (request, 'reservation.html', {
                'room': room, 
                'guest_id': guest_id, 
                'json_services': processed_all_services, 
                'services': Service.objects.all()
            }
        )
    else:
        target_reservations = room.reservation_set.all()
        reservations_json = serialize('json', target_reservations)  # Serialize QuerySet to JSON
        reservations_data = json.loads(reservations_json)
        for reservation in reservations_data:
            reservation['fields']['begin_date'] = reservation['fields']['begin_date'].split('T')[0]
            reservation['fields']['end_date'] = reservation['fields']['end_date'].split('T')[0]
        reservations_json_updated = json.dumps(reservations_data)
        # print(reservations_json_updated)
        return render(request, 'reservation.html', {
                'room': room, 
                'guest_id': guest_id, 
                'json_services': processed_all_services, 
                'services': Service.objects.all(), 
                'reservations': target_reservations, 
                'json_reservations': reservations_json_updated
            }
        )


def processReservation(request):
    guest_id = request.GET.get('guest_id')
    room_number = request.GET.get('room_number')
    print(guest_id, room_number)
    if request.method == 'POST':
        data = json.loads(request.body)
        begin_date = data.get('begin_date')
        end_date = data.get('end_date')
        pickup_time = data.get('pickup_time')
        dropoff_time = data.get('dropoff_time')
        selected_services = data.get('services', [])
        service_objects = Service.objects.filter(id__in=selected_services)

        print(guest_id, room_number, begin_date, end_date)

        updated_room = Room.objects.get(room_number=room_number)
        updated_room.is_available = False
        updated_room.save()

        print(begin_date, end_date, "000000000000000000000000000000000000000")
        if not(pickup_time and dropoff_time):
            pickup_time = None
            dropoff_time = None
        new_reservation = Reservation.objects.create(
            guest = Guest.objects.get(id=guest_id),
            room = updated_room,
            begin_date = begin_date,
            end_date = end_date,
            pickup_time = pickup_time,
            dropoff_time = dropoff_time,
        )
        new_reservation.services.add(*service_objects)

        print(new_reservation.begin_date)
        response_data = {
            'redirect_url': f'/dashboard/?guest_id={guest_id}'
        }
        return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid request'})


def is_six_hours_before_six_pm(end_date):
    current_time = datetime.now()
    target_time = datetime.combine(end_date, datetime.min.time()) + timedelta(hours=18)
    time_difference = target_time - current_time
    if time_difference.total_seconds() < (6 * 60 * 60):
        return True
    else:
        return False


def dashboard(request):
    guest_id = request.GET.get('guest_id')
    current_date = timezone.now().date()
    try:
        upcoming_reservation = Reservation.objects.filter(begin_date__gte=current_date, guest_id=guest_id).latest('begin_date')
    except:
        upcoming_reservation = None

    try:
        active_reservation = Reservation.objects.filter(begin_date__lte=current_date, end_date__gte=current_date, guest_id=guest_id).first()
        suggest_renewal = is_six_hours_before_six_pm(active_reservation.end_date)
    except:
        active_reservation = None
        suggest_renewal = False

    if guest_id:
        # print(guest_id, "0000000000000000000000000000000000000000000")
        guest = Guest.objects.get(id=guest_id)
        filtered_messages = Message.objects.filter(sender=guest, receiver=Guest.objects.get(id=1)) | Message.objects.filter(sender=Guest.objects.get(id=1), receiver=guest)
        # print(filtered_messages)
        target_reservations = Reservation.objects.filter(guest=guest)
        if target_reservations:
            return render(request, 'dashboard.html', {
                    'guest': guest, 
                    'reservations': target_reservations,
                    'upcoming_reservation': upcoming_reservation,
                    'active_reservation': active_reservation,
                    'messages': filtered_messages.order_by("date_time_sent"),
                    'suggest_renewal': suggest_renewal
                }
            )

        return render(request, 'dashboard.html', {
                    'guest': guest, 
                    'upcoming_reservation': upcoming_reservation,
                    'active_reservation': active_reservation,
                    'messages': filtered_messages.order_by("date_time_sent"),
                    'suggest_renewal': suggest_renewal
                }
            )
    else:
        guest = None
        return redirect(f'/loginUser')
    

def updatereservation(request):
    room_number = request.GET.get('room_number')
    guest_id = request.GET.get('guest_id')
    reservation_id = request.GET.get('reservation_id')
    target_reservation = Reservation.objects.get(id=reservation_id)
    room = Room.objects.get(room_number = room_number)

    user_chosen_services = target_reservation.services.all()
    user_chosen_services_json = serialize('json', user_chosen_services)  # Serialize QuerySet to JSON
    user_chosen_services_data = json.loads(user_chosen_services_json)
    processed_user_chosen_services = json.dumps(user_chosen_services_data)

    all_services = Service.objects.all()
    all_services_json = serialize('json', all_services)  # Serialize QuerySet to JSON
    all_services_data = json.loads(all_services_json)
    processed_all_services = json.dumps(all_services_data)

    target_reservations = room.reservation_set.all()
    reservations_json = serialize('json', target_reservations)  # Serialize QuerySet to JSON
    reservations_data = json.loads(reservations_json)
    for reservation in reservations_data:
        reservation['fields']['begin_date'] = reservation['fields']['begin_date'].split('T')[0]
        reservation['fields']['end_date'] = reservation['fields']['end_date'].split('T')[0]
    reservations_json_updated = json.dumps(reservations_data)
    # print(reservations_json_updated)
    return render(request, 'updatereservation.html', {
        'reservation_to_update': target_reservation,
        'room': room, 
        'guest_id': guest_id, 
        'reservations': target_reservations, 
        'json_reservations': reservations_json_updated,
        'services': Service.objects.all(),
        'json_services': processed_all_services,
        'user_chosen_services': processed_user_chosen_services,
    })


def process_update_reservation(request):
    reservation_id = request.GET.get('reservation_id')
    print(reservation_id, "0000000000000000000000000000000000000000000000000000000")
    guest_id = request.GET.get('guest_id')
    target_reservation = Reservation.objects.get(id=reservation_id)

    if request.method == 'POST':
        data = json.loads(request.body)
        begin_date = data.get('begin_date')
        end_date = data.get('end_date')
        selected_services = data.get('services', [])
        service_objects = Service.objects.filter(id__in=selected_services)

        print(begin_date, end_date, "55555555555555555555555555555555555555555555555555555555555555555")
        target_reservation.begin_date = begin_date
        target_reservation.end_date = end_date
        target_reservation.services.clear()
        target_reservation.services.add(*service_objects)
        target_reservation.save()

        response_data = {
            'redirect_url': f'/dashboard/?guest_id={guest_id}'
        }
        return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid request'})


def cancel_reservation(request):
    if request.method == 'POST':
        reservation_id = request.GET.get('reservation_id')
        reservation = Reservation.objects.get(id=reservation_id)
        # reservation.room.is_available = True
        Reservation.objects.filter(id=reservation_id).delete()
        return HttpResponse(status=204)  # Return a success response
    

def adminLogin(request):
    print(Guest.objects.all())
    return render(request, "adminlogin.html")


def processAdminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')


        user = authenticate(username=username, password=password)
        if user is not None:
            # Authentication successful
            return redirect(f'/admindashboard/?admin_id={user.id}')
        else:
            # Authentication failed
            return render(request, 'adminlogin.html', {'error_message': 'Invalid username or password.'})


def adminDashboard(request):
    admin_id = request.GET.get('admin_id')
    admin = Guest.objects.get(id=admin_id)
    return render(request, "admindashboard.html", {
            'admin': admin,
            'guests': Guest.objects.filter(is_staff=False),
            'reservations': Reservation.objects.all(),
            'rooms': Room.objects.all(),
            'messages': Message.objects.all().order_by("-date_time_sent"),
        }
    )


def adminCreateGuest(request):
    form = SignupForm()  # Create an instance of the SignupForm
    admin_id = request.GET.get('admin_id')
    if request.method == 'POST':
        form = SignupForm(request.POST)  # Bind form data to the request POST data

        if form.is_valid():
            email = form.cleaned_data['email']

            if Guest.objects.filter(email=email).exists():
                form.add_error('email', 'This email is already registered.')
            else:
                # Process the valid form data and create the guest object
                Guest.objects.create(
                    username=email,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=email,
                    password=form.cleaned_data['password'],
                    phone_number=form.cleaned_data['phone_number']
                )

                # Redirect to the roomspage page with the guest ID as a URL parameter
                return redirect(f'/admindashboard/?admin_id={admin_id}')

    return render(request, 'admincreateguest.html', {'form': form, 'admin_id': admin_id})


def adminUpdateGuest(request):
    form = SignupForm()  # Create an instance of the SignupForm
    admin_id = request.GET.get('admin_id')
    guest_id = request.GET.get('guest_id')

    target_guest = Guest.objects.get(id=guest_id)
    if request.method == 'POST':
        form = SignupForm(request.POST)  # Bind form data to the request POST data
        if form.is_valid():
            email = form.cleaned_data['email']
            print(form.cleaned_data)

            if Guest.objects.exclude(id=target_guest.id).filter(email=email).exists():
                form.add_error('email', 'This email is already registered.')
            else:
                # Process the valid form data and update the guest object
                target_guest.username=email,
                target_guest.first_name=form.cleaned_data['first_name']
                target_guest.last_name=form.cleaned_data['last_name']
                target_guest.email=email
                target_guest.password=form.cleaned_data['password']
                target_guest.phone_number=form.cleaned_data['phone_number']
                target_guest.save()

                # Redirect to the roomspage page with the guest ID as a URL parameter
                return redirect(f'/admindashboard/?admin_id={admin_id}')

    return render(request, 'adminupdateguest.html', {'form': form, 'admin_id': admin_id, 'guest': target_guest})


def adminDeleteGuest(request):
    admin_id = request.GET.get('admin_id')
    guest_id = request.GET.get('guest_id')

    try:
        guest = Guest.objects.get(id=guest_id)
        guest.delete()
        return redirect(f'/admindashboard/?admin_id={admin_id}')
    except Guest.DoesNotExist:
        # Handle the case when the guest doesn't exist
        return HttpResponse("Guest not found")


def adminCreateReservation(request):
    if request.method == 'POST':
        print(request.POST)
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            services = form.cleaned_data['services']
            print(services)
            airportservice = Service.objects.get(id=1)
            if airportservice in services:
                pickup_time = form.cleaned_data['pickup_time']
                dropoff_time = form.cleaned_data['dropoff_time']
                reservation.pickup_time = pickup_time
                reservation.dropoff_time = dropoff_time
            else:
                reservation.pickup_time = None
                reservation.dropoff_time = None

            print(reservation.begin_date, reservation.end_date, "0000000000000000000000000000000000000000000000000")
            reservation.save()
            form.save_m2m()
            return redirect('/admindashboard/?admin_id=1')
    else:
        form = ReservationForm()

    return render(request, 'admincreatereservation.html', {'form': form})


def adminDeleteReservation(request):
    admin_id = request.GET.get('admin_id')
    reservation_id = request.GET.get('reservation_id')

    try:
        reservation = Reservation.objects.get(id=reservation_id)
        # reservation.room.is_available = True
        reservation.delete()
        return redirect(f'/admindashboard/?admin_id={admin_id}')
    except Reservation.DoesNotExist:
        # Handle the case when the reservation doesn't exist
        return HttpResponse("Reservation not found")


def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sender = request.GET.get('sender')
        receiver = request.GET.get('receiver')
        print(sender, receiver, "666666666666666666666666666666666666666666666666666666666666")
        text = data.get('text')

        Message.objects.create(
            sender = Guest.objects.get(id=sender),
            receiver = Guest.objects.get(id=receiver),
            text = text
        )
        return JsonResponse({'ok': True})
    return JsonResponse({'error': 'Invalid request'})


def extend_reservation(request, reservation_id):
    # Retrieve the existing reservation object
    try:
        reservation = Reservation.objects.get(id=reservation_id)
    except Reservation.DoesNotExist:
        return JsonResponse({'error': 'Invalid reservation ID'})

    if request.method == 'POST':
        # Get the extension date from the request data
        data = json.loads(request.body)
        print(data)
        extension_date = data.get('extension_date')
        extension_date = datetime.strptime(extension_date, '%Y-%m-%d').date()
        print(extension_date)

        # Check if the extension date is before the current end date
        if extension_date <= reservation.end_date:
            return JsonResponse({'error': 'Extension date must be after the current end date'})

        # Check if there are any conflicting reservations for the room
        conflicting_reservations = Reservation.objects.filter(
            room=reservation.room,
            begin_date__lte=extension_date,
            end_date__gte=extension_date
        ).exclude(id=reservation_id)

        if conflicting_reservations.exists():
            return JsonResponse({'error': "Unfortunately, You can't renew your reservation for this room as it clashes with another reservation. You can try reserving another room instead"})

        # Update the reservation's end date to the new extension date
        reservation.end_date = extension_date
        reservation.save()

        return JsonResponse({'success': 'Reservation successfully extended'})

    return JsonResponse({'error': 'Invalid request method'})

