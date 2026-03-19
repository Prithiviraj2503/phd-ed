from django.contrib import admin
from .models import UserProfile, Department, Course, CourseContent, Assignment, Question, StudentAssignmentAttempt, StudentAnswer


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)


# Note: Course, CourseContent, Assignment, Question, StudentAssignmentAttempt, 
# and StudentAnswer are managed through custom app views, not Django admin
