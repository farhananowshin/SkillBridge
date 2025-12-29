from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from django.utils import timezone

# PDF Generation Imports
from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML, CSS # PDF তৈরির জন্য WeasyPrint
from django.conf import settings # Static ফাইল ব্যবহারের জন্য

# মডেল ইমপোর্ট (সবগুলো মডেল দরকার)
from .models import Course, Enrollment, Lesson, Assignment, Submission, Quiz, QuizResult, Question, Choice, User
# ফর্ম ইমপোর্ট
from .forms import StudentRegistrationForm, StudentProfileUpdateForm, AssignmentSubmissionForm 

# 1. Home Page View
def home(request):
    courses = Course.objects.all()
    return render(request, 'home.html', {'courses': courses})

# 2. Course List View (Search & Filter Logic সহ)
def course_list(request):
    courses = Course.objects.all()
    
    # --- Search Logic ---
    search_query = request.GET.get('q')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(mentor__first_name__icontains=search_query) |
            Q(mentor__last_name__icontains=search_query)
        ).distinct()

    # --- Filter Logic (Filter by Mentor) ---
    mentor_id = request.GET.get('mentor')
    if mentor_id:
        courses = courses.filter(mentor_id=mentor_id)

    # এনরোল্ড কোর্স আইডি লিস্ট
    enrolled_courses_ids = []
    if request.user.is_authenticated:
        enrolled_courses_ids = Enrollment.objects.filter(student=request.user).values_list('course__id', flat=True)
    
    # মেন্টর লিস্ট ফিল্টার ড্রপডাউনের জন্য
    mentors = User.objects.filter(role='mentor')
        
    return render(request, 'course_list.html', {
        'courses': courses,
        'enrolled_courses_ids': enrolled_courses_ids,
        'mentors': mentors,
        'search_query': search_query,
        'selected_mentor': mentor_id
    })

# 3. Student Registration View
def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'student'
            user.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('student_login') 
        else:
            return render(request, 'auth_split.html', {'register_form': form})
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'auth_split.html', {'register_form': form})

# 4. Student Login View
def student_login(request):
    register_form = StudentRegistrationForm()

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome back, {username}!")
                return redirect('course_list')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'auth_split.html', {'form': form, 'register_form': register_form})

# 5. Logout View
def student_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

# 6. Student Profile View
@login_required
def student_profile(request):
    if request.method == 'POST':
        form = StudentProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('student_profile') 
    else:
        form = StudentProfileUpdateForm(instance=request.user)
    
    return render(request, 'student_profile.html', {'form': form})

# 7. Course Detail View 
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    
    lessons = course.lessons.all() 
    assignments = course.assignments.all()
    quizzes = course.quizzes.all()

    return render(request, 'course_detail.html', {
        'course': course, 
        'is_enrolled': is_enrolled,
        'lessons': lessons,
        'assignments': assignments,
        'quizzes': quizzes
    })

# 8. Enroll Course View
@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.user.role != 'student':
        messages.error(request, "Only students can enroll in a course.")
        return redirect('course_detail', course_id=course_id)

    already_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    
    if not already_enrolled:
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, f"Successfully enrolled in {course.title}!")
    else:
        messages.info(request, "You are already enrolled in this course.")
        
    return redirect('course_detail', course_id=course.id)

# 9. Student Dashboard View 
@login_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    submissions = Submission.objects.filter(student=request.user).order_by('-submitted_at')
    quiz_results = QuizResult.objects.filter(student=request.user).order_by('-attempted_at')
    
    context = {
        'enrollments': enrollments,
        'submissions': submissions,
        'quiz_results': quiz_results
    }
    return render(request, 'student_dashboard.html', context)

# 10. Lesson Detail View
@login_required
def lesson_detail(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, "You must enroll in this course to view lessons.")
        return redirect('course_detail', course_id=course.id)

    next_lesson = Lesson.objects.filter(course=course, order__gt=lesson.order).order_by('order').first()
    previous_lesson = Lesson.objects.filter(course=course, order__lt=lesson.order).order_by('-order').first()

    return render(request, 'lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'next_lesson': next_lesson,
        'previous_lesson': previous_lesson
    })

# 11. Assignment Detail & Submission View
@login_required
def assignment_detail(request, course_id, assignment_id):
    course = get_object_or_404(Course, id=course_id)
    assignment = get_object_or_404(Assignment, id=assignment_id, course=course)
    
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, "You must enroll in this course to submit assignments.")
        return redirect('course_detail', course_id=course.id)

    submission = Submission.objects.filter(assignment=assignment, student=request.user).first()

    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.assignment = assignment
            sub.student = request.user
            sub.save()
            messages.success(request, "Assignment submitted successfully! 🎉")
            return redirect('assignment_detail', course_id=course.id, assignment_id=assignment.id)
    else:
        form = AssignmentSubmissionForm(instance=submission)

    return render(request, 'assignment_detail.html', {
        'course': course,
        'assignment': assignment,
        'submission': submission,
        'form': form
    })

# 12. Mentor Grading View
@login_required
def assignment_submissions(request, course_id, assignment_id):
    course = get_object_or_404(Course, id=course_id)
    assignment = get_object_or_404(Assignment, id=assignment_id, course=course)

    if request.user != course.mentor:
        messages.error(request, "Access Denied. You are not the mentor of this course.")
        return redirect('course_detail', course_id=course.id)

    submissions = Submission.objects.filter(assignment=assignment)

    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        marks = request.POST.get('marks')
        
        if submission_id and marks:
            sub = get_object_or_404(Submission, id=submission_id)
            sub.marks = marks
            sub.save()
            messages.success(request, f"Marks updated for {sub.student.username}!")
            return redirect('assignment_submissions', course_id=course.id, assignment_id=assignment.id)

    return render(request, 'assignment_submissions.html', {
        'course': course,
        'assignment': assignment,
        'submissions': submissions
    })

# 13. Take Quiz View
@login_required
def take_quiz(request, course_id, quiz_id):
    course = get_object_or_404(Course, id=course_id)
    quiz = get_object_or_404(Quiz, id=quiz_id, course=course)
    
    existing_result = QuizResult.objects.filter(student=request.user, quiz=quiz).first()
    if existing_result:
        return render(request, 'quiz_result.html', {
            'course': course,
            'quiz': quiz,
            'result': existing_result,
            'already_taken': True
        })

    if request.method == 'POST':
        score = 0
        total_questions = quiz.questions.count()
        
        for question in quiz.questions.all():
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                choice = Choice.objects.get(id=selected_choice_id)
                if choice.is_correct:
                    score += 1
        
        final_score = score
        
        result = QuizResult.objects.create(
            quiz=quiz,
            student=request.user,
            score=final_score
        )
        
        messages.success(request, f"Quiz submitted! You scored {final_score}")
        return render(request, 'quiz_result.html', {
            'course': course,
            'quiz': quiz,
            'result': result,
            'already_taken': False
        })

    return render(request, 'take_quiz.html', {
        'course': course,
        'quiz': quiz
    })

# 14. Generate Certificate View (নতুন যোগ করা হলো)
@login_required
def generate_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    
    
    
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, "You are not enrolled in this course.")
        return redirect('course_detail', course_id=course.id)

    
    total_assignments = Assignment.objects.filter(course=course).count()
    submitted_assignments = Submission.objects.filter(
        student=request.user, 
        assignment__course=course
    ).count()

 
    if total_assignments > 0 and submitted_assignments < total_assignments:
        messages.error(request, "Please complete and submit all assignments before getting the certificate.")
        return redirect('course_detail', course_id=course.id)

    
    total_quizzes = Quiz.objects.filter(course=course).count()
    attempted_quizzes = QuizResult.objects.filter(student=request.user, quiz__course=course).count()
    if total_quizzes > 0 and attempted_quizzes < total_quizzes:
        messages.error(request, "Please attempt all quizzes before getting the certificate.")
        return redirect('course_detail', course_id=course.id)
        
  
    
    template = get_template('certificate_template.html')
    html_content = template.render({
        'student_name': f"{request.user.first_name} {request.user.last_name}",
        'course_title': course.title,
        'mentor_name': f"{course.mentor.first_name} {course.mentor.last_name}",
        'completion_date': timezone.now().date(),
    })
    
  
    pdf_file = HTML(string=html_content).write_pdf() 
    
   
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{course.title}_{request.user.username}.pdf"'
    return response
def about(request):
    return render(request, 'about.html')

def terms(request):
    return render(request, 'terms.html')

def privacy(request):
    return render(request, 'privacy.html')