from django.contrib import admin
from .models import (
    Cat, AdoptionRequest, Donation, RescueRequest,
    LostFoundReport, Appointment, ChatMessage, UserProfile, HomeBanner
)


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order', 'cat')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle')


admin.site.register(Cat)
admin.site.register(AdoptionRequest)
admin.site.register(Donation)
admin.site.register(RescueRequest)
admin.site.register(LostFoundReport)
admin.site.register(Appointment)
admin.site.register(ChatMessage)
admin.site.register(UserProfile)