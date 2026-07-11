from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ============ CAT MODEL ============
class Cat(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available for Adoption'),
        ('Adopted', 'Already Adopted'),
        ('Rescue', 'In Rescue'),
        ('Medical', 'Under Medical Care'),
    ]
    
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    age = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to='cats/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    date_added = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class HomeBanner(models.Model):
    title = models.CharField(max_length=120, blank=True)
    subtitle = models.CharField(max_length=220, blank=True)
    image = models.ImageField(upload_to='banners/', blank=True, null=True)
    cat = models.ForeignKey(Cat, on_delete=models.SET_NULL, null=True, blank=True, related_name='home_banners')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title or f'Banner {self.id}'

# ============ USER PROFILE MODEL (for roles) ============
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('User', 'Regular User'),
        ('Volunteer', 'Volunteer'),
        ('Admin', 'Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    latitude = models.FloatField(blank=True, null=True)  # For location-based matching
    longitude = models.FloatField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

# ============ ADOPTION REQUEST MODEL ============
class AdoptionRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending Review'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Adoption Completed'),
    ]
    
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE, related_name='adoption_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adoption_requests', null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    date_submitted = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_adoptions')
    reviewed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Request for {self.cat.name} by {self.name}"

# ============ RESCUE REQUEST MODEL ============
class RescueRequest(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High Priority - Urgent'),
        ('Medium', 'Medium Priority'),
        ('Low', 'Low Priority'),
    ]
    
    STATUS_CHOICES = [
        ('Reported', 'Newly Reported'),
        ('Assigned', 'Assigned to Volunteer'),
        ('In Progress', 'Rescue In Progress'),
        ('Rescued', 'Successfully Rescued'),
        ('Completed', 'Case Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rescue_reports')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Reported')
    
    assigned_volunteer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_rescues')
    image = models.ImageField(upload_to='rescue/', blank=True, null=True)
    
    urgency_reason = models.TextField(blank=True, help_text="Why is this high priority?")
    date_reported = models.DateTimeField(auto_now_add=True)
    date_assigned = models.DateTimeField(null=True, blank=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"[{self.priority}] {self.title}"

# ============ LOST & FOUND MODEL ============
class LostFoundReport(models.Model):
    TYPE_CHOICES = [
        ('Lost', 'Lost Cat'),
        ('Found', 'Found Cat'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active - Still Searching'),
        ('Found', 'Found/Reunited'),
        ('Closed', 'Case Closed'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lostfound_reports')
    report_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    cat_name = models.CharField(max_length=100, blank=True)
    cat_description = models.TextField()
    breed = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    image = models.ImageField(upload_to='lostfound/')
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    
    date_reported = models.DateTimeField(auto_now_add=True)
    date_resolved = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"[{self.report_type}] {self.color} cat - {self.status}"

# ============ APPOINTMENT MODEL ============
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('No Show', 'No Show'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE, related_name='appointments')
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_appointments')

    def __str__(self):
        return f"Appointment: {self.user.username} - {self.cat.name}"

# ============ CHAT MESSAGE MODEL ============
class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    rescue_request = models.ForeignKey(RescueRequest, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_messages')

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"

# ============ DONATION MODEL ============
class Donation(models.Model):
    DONATION_TYPES = [
        ('Food', 'Food Supply'),
        ('Medical', 'Medical Care'),
        ('General', 'General Fund'),
        ('Equipment', 'Equipment & Supplies'),
        ('Shelter', 'Shelter Maintenance'),
    ]
    
    donor_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    donor_name = models.CharField(max_length=100)
    donor_email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPES, default='General')
    message = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True, unique=True, null=True)
    is_anonymous = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.donor_name} - {self.amount} PKR"
