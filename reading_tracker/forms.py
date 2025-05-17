from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Book, ReadingSession, ReadingGoal

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['is_public', 'bio', 'profile_picture']

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'total_pages', 'genre', 'status', 'cover_image']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'genre': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ReadingSessionForm(forms.ModelForm):
    class Meta:
        model = ReadingSession
        fields = ['book', 'pages_read', 'start_time', 'end_time', 'notes']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class ReadingGoalForm(forms.ModelForm):
    class Meta:
        model = ReadingGoal
        fields = ['goal_type', 'target_pages', 'target_books', 'start_date', 'end_date']
        widgets = {
            'goal_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.") 