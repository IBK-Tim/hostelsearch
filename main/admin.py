from django.contrib import admin
from .models import Student, Agent, Hostel, Review

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'matric_no', 'phone', 'created_at']
    search_fields = ['user__email', 'matric_no']

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display  = ['user', 'phone', 'is_verified', 'created_at']
    list_filter   = ['is_verified']
    readonly_fields = ['passport', 'id_document']

@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ['hostel_name', 'agent', 'hostel_type', 'price_session', 'status']
    list_filter  = ['status', 'hostel_type']
    list_editable = ['status']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['student', 'hostel', 'rating', 'created_at']