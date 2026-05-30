from django.urls import path
from . import views

urlpatterns = [
    # ============ HOME & ABOUT ============
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # ============ AUTHENTICATION ============
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # ============ DASHBOARD & PROFILE ============
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # ============ ADOPTION ============
    path('adopt/<int:cat_id>/', views.adopt_cat, name='adopt_cat'),
    path('cat/<int:cat_id>/', views.cat_detail, name='cat_detail'),
    path('adoption/success/<int:adoption_id>/', views.adoption_success, name='adoption_success'),
    
    # ============ RESCUE REQUESTS ============
    path('rescue/report/', views.report_rescue, name='report_rescue'),
    path('rescue/list/', views.rescue_list, name='rescue_list'),
    path('rescue/<int:rescue_id>/', views.rescue_detail, name='rescue_detail'),
    path('rescue/<int:rescue_id>/update-status/', views.update_rescue_status, name='update_rescue_status'),
    
    # ============ LOST & FOUND ============
    path('lostfound/report/', views.report_lostfound, name='report_lostfound'),
    path('lostfound/list/', views.lostfound_list, name='lostfound_list'),
    path('lostfound/<int:report_id>/', views.lostfound_detail, name='lostfound_detail'),
    path('lostfound/<int:report_id>/resolved/', views.lostfound_resolved, name='lostfound_resolved'),
    
    # ============ APPOINTMENTS ============
    path('appointment/book/<int:cat_id>/', views.book_appointment, name='book_appointment'),
    path('appointment/success/<int:appointment_id>/', views.appointment_success, name='appointment_success'),
    path('appointments/my/', views.my_appointments, name='my_appointments'),
    
    # ============ CHAT ============
    path('chat/message/<int:recipient_id>/', views.send_message, name='send_message'),
    path('chat/message/<int:recipient_id>/rescue/<int:rescue_id>/', views.send_message, name='send_message_rescue'),
    path('chat/conversation/<int:user_id>/', views.conversation, name='conversation'),
    path('chat/inbox/', views.inbox, name='inbox'),
    
    # ============ DONATIONS ============
    path('donate/', views.donate, name='donate'),
    path('donation/success/<int:donation_id>/', views.donation_success, name='donation_success'),
    path('donations/list/', views.donations_list, name='donations_list'),
    
    # ============ ADMIN PANEL ============
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/adoptions/', views.admin_adoptions, name='admin_adoptions'),
    path('admin/adoption/<int:adoption_id>/review/', views.admin_review_adoption, name='admin_review_adoption'),
    path('admin/rescues/', views.admin_rescues, name='admin_rescues'),
]