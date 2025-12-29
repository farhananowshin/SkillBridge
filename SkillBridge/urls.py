from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views  

urlpatterns = [
    # --- 1. Admin Path ---
    path('admin/', admin.site.urls),
    
    # --- 2. Home Path ---
    path('', views.home, name='home'), 
    
    # --- 3. Authentication Paths ---
    path('login/', views.student_login, name='student_login'),
    path('register/', views.student_register, name='student_register'),
    path('logout/', views.student_logout, name='student_logout'),
    
    # --- 4. Core App Paths ---
    path('courses/', views.course_list, name='course_list'),
    path('profile/', views.student_profile, name='student_profile'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),

    # --- 5. Course Interaction Paths ---
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    
    # Lessons
    path('course/<int:course_id>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    
    # Assignments
    path('course/<int:course_id>/assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('course/<int:course_id>/assignment/<int:assignment_id>/submissions/', views.assignment_submissions, name='assignment_submissions'),
    
    # Quiz
    path('course/<int:course_id>/quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    
    # Certificate
    path('course/<int:course_id>/certificate/', views.generate_certificate, name='generate_certificate'),

    # --- 6. Footer Pages ---
    path('about/', views.about, name='about'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)