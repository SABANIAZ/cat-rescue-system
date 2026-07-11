from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q, Sum
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2

from .models import (
    Cat, UserProfile, AdoptionRequest, RescueRequest, 
    LostFoundReport, Appointment, ChatMessage, Donation, HomeBanner
)
from .forms import (
    UserRegistrationForm, UserLoginForm, AdoptionForm, RescueRequestForm,
    LostFoundForm, AppointmentForm, ChatMessageForm, DonationForm, UserProfileForm
)

# ============ HAVERSINE FORMULA for Location-Based Matching ============
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers"""
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

# ============ AUTHENTICATION VIEWS ============
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create user profile with role
            UserProfile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', '')
            )
            
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = UserLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

# ============ HOME & ABOUT PAGES ============
def home(request):
    cats = Cat.objects.all()
    rescue_count = RescueRequest.objects.filter(status__in=['Rescued', 'Completed']).count()
    adoption_count = AdoptionRequest.objects.filter(status='Completed').count()
    home_slides = HomeBanner.objects.filter(is_active=True).order_by('order', 'id')
    home_cats = cats.exclude(status__in=['Adopted', 'Rescue'])
    
    context = {
        'cats': cats,
        'rescue_count': rescue_count,
        'adoption_count': adoption_count,
        'home_slides': home_slides,
        'available_cats': home_cats,
    }
    return render(request, 'home.html', context)

def about(request):
    rescued_cats_count = Cat.objects.filter(status='Rescue').count()
    successful_adoptions_count = Cat.objects.filter(status='Adopted').count()
    happy_families_count = Cat.objects.filter(status='Adopted').count()
    about_cats = Cat.objects.filter(status__in=['Adopted', 'Rescue'])

    context = {
        'rescued_cats_count': rescued_cats_count,
        'successful_adoptions_count': successful_adoptions_count,
        'happy_families_count': happy_families_count,
        'about_cats': about_cats,
    }
    return render(request, 'about.html', context)

# ============ DASHBOARD (USER PROFILE) ============
@login_required(login_url='login')
def dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'User'})
    
    context = {
        'profile': profile,
        'adoption_requests': AdoptionRequest.objects.filter(user=request.user),
        'rescue_requests': RescueRequest.objects.filter(reporter=request.user),
        'appointments': Appointment.objects.filter(user=request.user),
        'donations': Donation.objects.filter(donor_user=request.user),
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def profile_edit(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'User'})
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'profile_edit.html', {'form': form})

# ============ ADOPTION MANAGEMENT ============
@login_required(login_url='login')
def adopt_cat(request, cat_id):
    cat = get_object_or_404(Cat, id=cat_id)
    
    if request.method == 'POST':
        form = AdoptionForm(request.POST)
        if form.is_valid():
            adoption_request = form.save(commit=False)
            adoption_request.cat = cat
            adoption_request.user = request.user
            adoption_request.save()
            return redirect('adoption_success', adoption_id=adoption_request.id)
    else:
        form = AdoptionForm()
    
    return render(request, 'adopt_form.html', {'form': form, 'cat': cat})


def cat_detail(request, cat_id):
    """Display a full detail page for a cat."""
    cat = get_object_or_404(Cat, id=cat_id)
    return render(request, 'cat/detail.html', {'cat': cat})

def adoption_success(request, adoption_id):
    adoption = get_object_or_404(AdoptionRequest, id=adoption_id)
    return render(request, 'adoption_success.html', {'adoption': adoption})

# ============ RESCUE REQUEST MANAGEMENT ============
@login_required(login_url='login')
def report_rescue(request):
    if request.method == 'POST':
        form = RescueRequestForm(request.POST, request.FILES)
        if form.is_valid():
            rescue_request = form.save(commit=False)
            rescue_request.reporter = request.user
            
            # Auto-assign priority based on urgency_reason
            if any(word in rescue_request.urgency_reason.lower() for word in ['urgent', 'bleeding', 'injured', 'trapped', 'emergency']):
                rescue_request.priority = 'High'
            
            rescue_request.save()
            
            # Find and assign nearby volunteers
            if rescue_request.latitude and rescue_request.longitude:
                assign_nearby_volunteers(rescue_request)
            
            return redirect('rescue_detail', rescue_id=rescue_request.id)
    else:
        form = RescueRequestForm()
    
    return render(request, 'rescue/report.html', {'form': form})

def assign_nearby_volunteers(rescue_request):
    """Find nearby volunteers and assign them"""
    volunteers = UserProfile.objects.filter(
        role='Volunteer',
        latitude__isnull=False,
        longitude__isnull=False
    )
    
    nearby = []
    for volunteer in volunteers:
        distance = haversine_distance(
            rescue_request.latitude, rescue_request.longitude,
            volunteer.latitude, volunteer.longitude
        )
        if distance <= 10:  # Within 10km
            nearby.append((volunteer, distance))
    
    # Sort by distance and assign first volunteer
    if nearby:
        nearest_volunteer = sorted(nearby, key=lambda x: x[1])[0][0]
        rescue_request.assigned_volunteer = nearest_volunteer.user
        rescue_request.status = 'Assigned'
        rescue_request.date_assigned = datetime.now()
        rescue_request.save()

@login_required(login_url='login')
def rescue_list(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == 'Volunteer':
        rescues = RescueRequest.objects.filter(assigned_volunteer=request.user)
    elif profile and profile.role == 'Admin':
        rescues = RescueRequest.objects.all()
    else:
        rescues = RescueRequest.objects.filter(reporter=request.user)
    
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    if status_filter:
        rescues = rescues.filter(status=status_filter)
    if priority_filter:
        rescues = rescues.filter(priority=priority_filter)
    
    return render(request, 'rescue/list.html', {'rescues': rescues})

@login_required(login_url='login')
def rescue_detail(request, rescue_id):
    rescue = get_object_or_404(RescueRequest, id=rescue_id)
    messages = ChatMessage.objects.filter(rescue_request=rescue).order_by('timestamp')
    
    return render(request, 'rescue/detail.html', {
        'rescue': rescue,
        'messages': messages,
    })

@login_required(login_url='login')
def update_rescue_status(request, rescue_id):
    rescue = get_object_or_404(RescueRequest, id=rescue_id)
    
    if request.user != rescue.reporter and request.user != rescue.assigned_volunteer:
        return redirect('rescue_detail', rescue_id=rescue_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(RescueRequest.STATUS_CHOICES):
            rescue.status = new_status
            if new_status in ['Rescued', 'Completed']:
                rescue.date_completed = datetime.now()
            rescue.save()
    
    return redirect('rescue_detail', rescue_id=rescue_id)

# ============ LOST & FOUND MANAGEMENT ============
@login_required(login_url='login')
def report_lostfound(request):
    if request.method == 'POST':
        form = LostFoundForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.save()
            return redirect('lostfound_detail', report_id=report.id)
    else:
        form = LostFoundForm()
    
    return render(request, 'lostfound/report.html', {'form': form})

def lostfound_list(request):
    reports = LostFoundReport.objects.filter(status='Active').order_by('-date_reported')
    report_type = request.GET.get('type')
    
    if report_type in ['Lost', 'Found']:
        reports = reports.filter(report_type=report_type)
    
    return render(request, 'lostfound/list.html', {'reports': reports})

@login_required(login_url='login')
def lostfound_detail(request, report_id):
    report = get_object_or_404(LostFoundReport, id=report_id)
    return render(request, 'lostfound/detail.html', {'report': report})

@login_required(login_url='login')
def lostfound_resolved(request, report_id):
    report = get_object_or_404(LostFoundReport, id=report_id)
    if request.user == report.reporter:
        report.status = 'Found'
        report.date_resolved = datetime.now()
        report.save()
    return redirect('lostfound_list')

# ============ APPOINTMENT MANAGEMENT ============
@login_required(login_url='login')
def book_appointment(request, cat_id):
    cat = get_object_or_404(Cat, id=cat_id)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.cat = cat
            appointment.save()
            return redirect('appointment_success', appointment_id=appointment.id)
    else:
        form = AppointmentForm()
        # Set minimum date to tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        form.fields['scheduled_date'].initial = tomorrow
    
    return render(request, 'appointment/book.html', {'form': form, 'cat': cat})

def appointment_success(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'appointment/success.html', {'appointment': appointment})

@login_required(login_url='login')
def my_appointments(request):
    appointments = Appointment.objects.filter(user=request.user).order_by('scheduled_date')
    return render(request, 'appointment/list.html', {'appointments': appointments})

# ============ CHAT SYSTEM ============
@login_required(login_url='login')
def send_message(request, recipient_id, rescue_id=None):
    recipient = get_object_or_404(User, id=recipient_id)
    rescue_request = None
    
    if rescue_id:
        rescue_request = get_object_or_404(RescueRequest, id=rescue_id)
    
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.rescue_request = rescue_request
            message.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'sent', 'message_id': message.id})
            
            if rescue_request:
                return redirect('rescue_detail', rescue_id=rescue_id)
            else:
                return redirect('conversation', user_id=recipient_id)
    else:
        form = ChatMessageForm()
    
    return render(request, 'chat/send.html', {
        'form': form,
        'recipient': recipient,
        'rescue': rescue_request
    })

@login_required(login_url='login')
def conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages = ChatMessage.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('timestamp')
    
    return render(request, 'chat/conversation.html', {
        'other_user': other_user,
        'messages': messages,
    })

@login_required(login_url='login')
def inbox(request):
    pairs = ChatMessage.objects.filter(
        Q(recipient=request.user) | Q(sender=request.user)
    ).values('sender', 'recipient').distinct()
    
    partner_ids = set()
    partners = []
    for item in pairs:
        partner_id = item['recipient'] if item['sender'] == request.user.id else item['sender']
        if partner_id not in partner_ids:
            partner_ids.add(partner_id)
            try:
                partners.append(User.objects.get(id=partner_id))
            except User.DoesNotExist:
                continue
    
    return render(request, 'chat/inbox.html', {'partners': partners})

# ============ DONATION SYSTEM ============
def donate(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            if request.user.is_authenticated:
                donation.donor_user = request.user
            donation.save()
            return redirect('donation_success', donation_id=donation.id)
    else:
        form = DonationForm()
        if request.user.is_authenticated:
            form.initial['donor_name'] = request.user.get_full_name() or request.user.username
            form.initial['donor_email'] = request.user.email
    
    return render(request, 'donation/donate.html', {'form': form})

def donation_success(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'donation/success.html', {'donation': donation})

def donations_list(request):
    donations = Donation.objects.filter(is_anonymous=False).order_by('-date')[:50]
    total_donations = Donation.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'donations': donations,
        'total_donations': total_donations,
    }
    return render(request, 'donation/list.html', context)

# ============ ADMIN PANEL ============
@login_required(login_url='login')
def admin_dashboard(request):
    if not (request.user.is_staff or hasattr(request.user, 'profile') and request.user.profile.role == 'Admin'):
        return redirect('dashboard')
    
    context = {
        'total_cats': Cat.objects.count(),
        'total_adoptions': AdoptionRequest.objects.count(),
        'pending_adoptions': AdoptionRequest.objects.filter(status='Pending').count(),
        'total_rescues': RescueRequest.objects.count(),
        'active_rescues': RescueRequest.objects.filter(status__in=['Reported', 'Assigned', 'In Progress']).count(),
        'total_donations': Donation.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_volunteers': UserProfile.objects.filter(role='Volunteer').count(),
    }
    return render(request, 'admin/dashboard.html', context)

@login_required(login_url='login')
def admin_adoptions(request):
    if not (request.user.is_staff or hasattr(request.user, 'profile') and request.user.profile.role == 'Admin'):
        return redirect('dashboard')
    
    adoptions = AdoptionRequest.objects.all()
    status_filter = request.GET.get('status')
    
    if status_filter:
        adoptions = adoptions.filter(status=status_filter)
    
    return render(request, 'admin/adoptions.html', {'adoptions': adoptions})

@login_required(login_url='login')
def admin_review_adoption(request, adoption_id):
    if not (request.user.is_staff or hasattr(request.user, 'profile') and request.user.profile.role == 'Admin'):
        return redirect('dashboard')
    
    adoption = get_object_or_404(AdoptionRequest, id=adoption_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['Approved', 'Rejected']:
            adoption.status = action
            adoption.reviewed_by = request.user
            adoption.reviewed_date = datetime.now()
            adoption.save()
            return redirect('admin_adoptions')
    
    return render(request, 'admin/review_adoption.html', {'adoption': adoption})

@login_required(login_url='login')
def admin_rescues(request):
    if not (request.user.is_staff or hasattr(request.user, 'profile') and request.user.profile.role == 'Admin'):
        return redirect('dashboard')
    
    rescues = RescueRequest.objects.all()
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    if status_filter:
        rescues = rescues.filter(status=status_filter)
    if priority_filter:
        rescues = rescues.filter(priority=priority_filter)
    
    return render(request, 'admin/rescues.html', {'rescues': rescues})
