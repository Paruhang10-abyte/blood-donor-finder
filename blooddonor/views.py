from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Donor, BloodRequest
from .algorithm import find_donors, NEPAL_DISTRICTS, DISTRICT_COORDS, is_valid_district
from django.db import IntegrityError
import random
import string
from django.core.paginator import Paginator

# HOME PAGE
def home(request):
    return render(request, 'home.html')

# REGISTER PAGE
def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        blood_group = request.POST['blood_group']
        district = request.POST['district']
        phone = request.POST['phone']

        if not email.endswith('@gmail.com'):
            return render(request, 'register.html', {
                'error': 'Invalid email!',
                'name': name,
                'email': email,
                'blood_group': blood_group,
                'district': district,
                'phone': phone,
                'districts': NEPAL_DISTRICTS,
            })

        if not phone.isdigit() or len(phone) != 10 or not phone.startswith('9'):
            return render(request, 'register.html', {
                'error': 'Invalid phone number! Must be 10 digits starting with 9 (e.g. 9812345678)',
                'name': name,
                'email': email,
                'blood_group': blood_group,
                'district': district,
                'phone': phone,
                'districts': NEPAL_DISTRICTS,
            })

        if not is_valid_district(district):
            return render(request, 'register.html', {
                'error': f'"{district}" is not a valid Nepal district.',
                'name': name,
                'email': email,
                'blood_group': blood_group,
                'district': district,
                'phone': phone,
                'districts': NEPAL_DISTRICTS,
            })

        if User.objects.filter(username=email).exists():
            return render(request, 'register.html', {
                'error': 'This email is already registered!',
                'name': name,
                'email': email,
                'blood_group': blood_group,
                'district': district,
                'phone': phone,
                'districts': NEPAL_DISTRICTS,
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        user.first_name = name
        user.save()

        Donor.objects.create(
            user=user,
            blood_group=blood_group,
            district=district,
            phone=phone
        )
        return redirect('/login/')

    return render(request, 'register.html', {'districts': NEPAL_DISTRICTS})

# LOGIN PAGE
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('/dashboard/')
        else:
            return render(request, 'login.html', {'error': 'Invalid email or password!'})
    return render(request, 'login.html')

# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('/')

# DASHBOARD
@login_required
def dashboard(request):
    try:
        donor = Donor.objects.get(user=request.user)
    except Donor.DoesNotExist:
        return redirect('/search/')
    requests = BloodRequest.objects.filter(donor=donor).order_by('-created_at')
    return render(request, 'dashboard.html', {
        'donor': donor,
        'requests': requests
    })

# SEARCH PAGE
def search(request):
    if request.method == 'POST':
        blood_group = request.POST['blood_group']
        district = request.POST.get('district', '')

        try:
            lat = float(request.POST.get('latitude', ''))
            lng = float(request.POST.get('longitude', ''))
        except ValueError:
            lat = None
            lng = None

        if lat is None and district:
            coords = DISTRICT_COORDS.get(district.strip().lower())
            if coords:
                lat, lng = coords

        all_results = find_donors(blood_group, lat, lng)
        paginator = Paginator(all_results, 10)
        page = request.GET.get('page', 1)
        results = paginator.get_page(page)
        return render(request, 'results.html', {
            'results': results,
            'blood_group': blood_group,
            'district': district,
            'lat': lat or '',
            'lng': lng or '',
        })
    return render(request, 'search.html', {'districts': NEPAL_DISTRICTS})

# TOGGLE AVAILABILITY
@login_required
def toggle(request):
    donor = Donor.objects.get(user=request.user)
    donor.is_available = not donor.is_available
    donor.save()
    return redirect('/dashboard/')

# REQUEST PAGE - patient sends blood request to specific donor
def submit_request(request, donor_id):
    donor = Donor.objects.get(id=donor_id)

    if request.method == 'POST':
        district = request.POST['district']

        if not is_valid_district(district):
            return render(request, 'request.html', {
                'donor': donor,
                'error': f'"{district}" is not a valid Nepal district.',
                'districts': NEPAL_DISTRICTS,
            })

        blood_group_needed = request.POST['blood_group_needed']
        original_blood_group = request.POST.get('original_blood_group', '').strip()
        blood_group_changed = bool(original_blood_group and blood_group_needed != original_blood_group)
        
        # one phone number can only have one pending request at a time
        existing = BloodRequest.objects.filter(
            phone=request.POST['phone'],
            status='Pending'
        ).exists()

        if existing:
            return render(request, 'request.html', {
                'donor': donor,
                'error': 'You already have a pending request. Please wait for the donor to respond or cancel your existing request first.',
                'districts': NEPAL_DISTRICTS,
                'prefill_blood_group': request.POST.get('blood_group_needed', ''),
                'prefill_district': request.POST.get('district', ''),
            })

        # generate unique token like BLD-482910
        token = 'BLD-' + ''.join(random.choices(string.digits, k=8))

        BloodRequest.objects.create(
            patient_name=request.POST['patient_name'],
            blood_group_needed=blood_group_needed,
            district=district,
            phone=request.POST['phone'],
            donor=donor,
            blood_group_changed=blood_group_changed,
            original_blood_group=original_blood_group,
            token=token,
        )
        return redirect(f'/request-sent/?token={token}')

    prefill_blood_group = request.GET.get('blood_group', '').strip()
    prefill_district = request.GET.get('district', '').strip()
    prefill_lat = request.GET.get('lat', '').strip()
    prefill_lng = request.GET.get('lng', '').strip()
    return render(request, 'request.html', {
        'donor': donor,
        'districts': NEPAL_DISTRICTS,
        'prefill_blood_group': prefill_blood_group,
        'prefill_district': prefill_district,
        'prefill_lat': prefill_lat,
        'prefill_lng': prefill_lng,
    })

# REQUEST SENT PAGE - shows token to patient
def request_sent(request):
    token = request.GET.get('token', '')
    return render(request, 'request_sent.html', {'token': token})

# DONOR ACCEPTS OR REJECTS BLOOD REQUEST
@login_required
def update_request(request, request_id, status):
    donor = Donor.objects.get(user=request.user)
    blood_request = BloodRequest.objects.get(id=request_id, donor=donor)
    blood_request.status = status
    blood_request.save()
    return redirect('/dashboard/')

# PATIENT CHECKS BLOOD REQUEST STATUS BY TOKEN
def check_status(request):
    result = None
    token = None
    error = None
    if request.method == 'POST':
        token = request.POST['token'].strip().upper()
        try:
            result = BloodRequest.objects.get(token=token)
        except BloodRequest.DoesNotExist:
            error = f'No request found for token {token}. Please check and try again.'
    return render(request, 'check_status.html', {
        'result': result,
        'token': token,
        'error': error,
    })

# UPDATE PROFILE
@login_required
def update_profile(request):
    donor = Donor.objects.get(user=request.user)

    if request.method == 'POST':
        district = request.POST['district']
        phone = request.POST['phone']
        blood_group = request.POST['blood_group']

        if not phone.isdigit() or len(phone) != 10 or not phone.startswith('9'):
            return render(request, 'update_profile.html', {
                'donor': donor,
                'error': 'Invalid phone number! Must be 10 digits starting with 9.',
                'districts': NEPAL_DISTRICTS,
            })
        if not is_valid_district(district):
            return render(request, 'update_profile.html', {
                'donor': donor,
                'error': f'"{district}" is not a valid Nepal district.',
                'districts': NEPAL_DISTRICTS,
            })

        donor.district = district
        donor.phone = phone
        donor.blood_group = blood_group
        donor.save()

        return redirect('/dashboard/')

    return render(request, 'update_profile.html', {
        'donor': donor,
        'districts': NEPAL_DISTRICTS,
    })
    
# CANCEL REQUEST - patient cancels their pending request
def cancel_request(request, request_id):
    if request.method == 'POST':
        token = request.POST.get('token', '').strip().upper()
        try:
            blood_request = BloodRequest.objects.get(id=request_id, token=token, status='Pending')
            blood_request.delete()
        except BloodRequest.DoesNotExist:
            pass
    return redirect('/check-status/?cancelled=true')