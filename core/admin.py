from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Course, Enrollment, Assignment, Submission, Lesson, Quiz, Question, Choice, QuizResult


class CustomUserAdmin(UserAdmin):
    model = User
    

    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('role', 'profile_photo', 'student_id', 'phone_number', 'department', 'semester')}),
    )
    
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']

admin.site.register(User, CustomUserAdmin)

# 2. Course Admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'mentor', 'created_at')
    search_fields = ('title',)

# 3. Lesson Admin
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'video_url')
    list_filter = ('course',)
    ordering = ('course', 'order')

# 4. Enrollment Admin
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')

# 5. Assignment Admin
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date')

# 6. Submission Admin
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at')

# --- Quiz Admin Setup ---

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')
    inlines = [ChoiceInline]

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'total_marks')

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'attempted_at')