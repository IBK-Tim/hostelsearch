from django.contrib import admin
from .models import Student, Agent, Hostel, Review
from django.utils.html import format_html

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'matric_no', 'phone', 'created_at']
    search_fields = ['user__email', 'matric_no']

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display  = ['user', 'business_name', 'phone', 'is_verified', 'created_at']
    list_filter   = ['is_verified']

    def passport_preview(self, obj):
        if obj.passport:
            url = obj.passport.url
            return format_html('<a href="{}" target="_blank"><img src="{}" width="100" height="100" style="object-fit:cover;border-radius:8px;"/></a>', url, url)
        return 'No passport uploaded'
    passport_preview.short_description = 'Passport'

    def nin_preview(self, obj):
        if obj.id_document:
            url = obj.id_document.url
            return format_html('<a href="{}" target="_blank"><img src="{}" width="200" style="border-radius:8px;"/></a>', url, url)
        return 'No NIN uploaded'
    nin_preview.short_description = 'NIN Document'

    readonly_fields = ['passport_preview', 'nin_preview']
    fields = ['user', 'phone', 'business_name', 'is_verified', 'passport_preview', 'nin_preview']

@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ['hostel_name', 'agent', 'hostel_type', 'price_session', 'status']
    list_filter  = ['status', 'hostel_type']
    list_editable = ['status']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['student', 'hostel', 'rating', 'created_at']