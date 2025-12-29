from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, Submission 


class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 
            'profile_photo', 'phone_number', 
            'department', 'student_id', 
            'dob', 'gender', 'address'
        ]
        
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
           
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file'] 
        
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': '.pdf,.doc,.docx,.zip' 
            }),
        }