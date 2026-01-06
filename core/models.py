from urllib.parse import urlparse, parse_qs
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
    )
    DEPT_CHOICES = (
        ('CSE', 'Computer Science & Engineering'),
        ('SWE', 'Software Engineering'),
        ('EEE', 'Electrical & Electronic Engineering'),
        ('BBA', 'Business Administration'),
        ('OTHER', 'Other'),
    )
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    TRACK_CHOICES = (
        ('web', 'Web Development'),
        ('data', 'Data Science'),
        ('network', 'Networking'),
        ('app', 'App Development'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(null=True, blank=True, help_text="Date of Birth")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    student_id = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=10, choices=DEPT_CHOICES, blank=True, null=True)
    semester = models.CharField(max_length=20, blank=True, null=True)
    preferred_track = models.CharField(max_length=20, choices=TRACK_CHOICES, blank=True, null=True)
    learning_goal = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username


# 2. Course Model 
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    mentor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mentored_courses',
        limit_choices_to={'role': 'mentor'},
    )
    
    course_image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# 3. Lesson Model 
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    video_url = models.URLField(max_length=300, blank=True, null=True)
    content = models.TextField()
    order = models.IntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def _extract_youtube_id(self, url: str):
        if not url: return None
        url = url.strip()
        if 'youtu.be' in url:
            return url.split('/')[-1].split('?')[0]
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        if 'v' in qs:
            return qs['v'][0]
        if 'embed' in url:
            return url.split('/')[-1].split('?')[0]
        return url.split('/')[-1]

    def save(self, *args, **kwargs):
        if self.video_url:
            vid = self._extract_youtube_id(self.video_url)
            if vid:
                self.video_url = f"https://www.youtube.com/embed/{vid}"
        super().save(*args, **kwargs)


# 4. Enrollment Model
class Enrollment(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'},
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


# 5. Assignment Model
class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()

    def __str__(self):
        return self.title


# 6. Submission Model
class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
    )
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    marks = models.IntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.title}"


# 7. Quiz Model
class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField()
    total_marks = models.IntegerField(default=10)

    def __str__(self):
        return self.title

# --- Question & Choice Models ---
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.IntegerField(default=1)

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
# --------------------------------

# 8. Quiz Result Model
class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
    )
    score = models.IntegerField()
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'quiz')

    def __str__(self):
        return f"{self.student.username}'s score: {self.score} on {self.quiz.title}"