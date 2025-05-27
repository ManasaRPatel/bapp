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
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'total_pages': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'})
        }

    def clean_total_pages(self):
        total_pages = self.cleaned_data.get('total_pages')
        if total_pages <= 0:
            raise forms.ValidationError("Total pages must be greater than 0.")
        return total_pages

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if isbn:
            # Remove any hyphens or spaces from ISBN
            isbn = ''.join(c for c in isbn if c.isdigit())
            if len(isbn) not in [10, 13]:
                raise forms.ValidationError("ISBN must be 10 or 13 digits.")
        return isbn

class ReadingSessionForm(forms.ModelForm):
    class Meta:
        model = ReadingSession
        fields = ['pages_read', 'start_time', 'end_time', 'notes']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'pages_read': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def clean_pages_read(self):
        pages_read = self.cleaned_data.get('pages_read')
        if pages_read <= 0:
            raise forms.ValidationError("Pages read must be greater than 0.")
        return pages_read

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError("End time must be after start time.")
            
            # Check if the duration is reasonable (e.g., less than 24 hours)
            duration = end_time - start_time
            if duration.total_seconds() > 86400:  # 24 hours in seconds
                raise forms.ValidationError("Reading session duration cannot exceed 24 hours.")
        
        return cleaned_data

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