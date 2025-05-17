from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Book, ReadingSession, ReadingGoal, UserProfile
from .forms import (UserRegistrationForm, UserProfileForm, BookForm,
                   ReadingSessionForm, ReadingGoalForm)

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'reading_tracker/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Reading Tracker.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'reading_tracker/register.html', {'form': form})

@login_required
def dashboard(request):
    # Get user's reading statistics
    total_books = Book.objects.filter(user=request.user).count()
    books_completed = Book.objects.filter(user=request.user, status='CO').count()
    current_books = Book.objects.filter(user=request.user, status='CR')
    
    # Calculate pages read in the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_sessions = ReadingSession.objects.filter(
        user=request.user,
        start_time__gte=thirty_days_ago
    )
    pages_last_30_days = recent_sessions.aggregate(Sum('pages_read'))['pages_read__sum'] or 0
    
    # Get active reading goals
    active_goals = ReadingGoal.objects.filter(
        user=request.user,
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    )
    
    context = {
        'total_books': total_books,
        'books_completed': books_completed,
        'current_books': current_books,
        'pages_last_30_days': pages_last_30_days,
        'active_goals': active_goals,
    }
    return render(request, 'reading_tracker/dashboard.html', context)

@login_required
def profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'reading_tracker/profile.html', {'profile': profile})

@login_required
def edit_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'reading_tracker/edit_profile.html', {'form': form})

@login_required
def book_list(request):
    books = Book.objects.filter(user=request.user)
    return render(request, 'reading_tracker/book_list.html', {'books': books})

@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            book.save()
            messages.success(request, 'Book added successfully.')
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'reading_tracker/add_book.html', {'form': form})

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk, user=request.user)
    sessions = ReadingSession.objects.filter(book=book).order_by('-start_time')
    return render(request, 'reading_tracker/book_detail.html', {
        'book': book,
        'sessions': sessions
    })

@login_required
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully.')
            return redirect('book_detail', pk=pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'reading_tracker/edit_book.html', {'form': form, 'book': book})

@login_required
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk, user=request.user)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully.')
        return redirect('book_list')
    return render(request, 'reading_tracker/delete_book.html', {'book': book})

@login_required
def add_reading_session(request):
    if request.method == 'POST':
        form = ReadingSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user
            session.save()
            messages.success(request, 'Reading session added successfully.')
            return redirect('book_detail', pk=session.book.pk)
    else:
        form = ReadingSessionForm()
        form.fields['book'].queryset = Book.objects.filter(user=request.user)
    return render(request, 'reading_tracker/add_session.html', {'form': form})

@login_required
def session_detail(request, pk):
    session = get_object_or_404(ReadingSession, pk=pk, user=request.user)
    return render(request, 'reading_tracker/session_detail.html', {'session': session})

@login_required
def edit_session(request, pk):
    session = get_object_or_404(ReadingSession, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ReadingSessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reading session updated successfully.')
            return redirect('session_detail', pk=pk)
    else:
        form = ReadingSessionForm(instance=session)
        form.fields['book'].queryset = Book.objects.filter(user=request.user)
    return render(request, 'reading_tracker/edit_session.html', {'form': form, 'session': session})

@login_required
def delete_session(request, pk):
    session = get_object_or_404(ReadingSession, pk=pk, user=request.user)
    if request.method == 'POST':
        book_pk = session.book.pk
        session.delete()
        messages.success(request, 'Reading session deleted successfully.')
        return redirect('book_detail', pk=book_pk)
    return render(request, 'reading_tracker/delete_session.html', {'session': session})

@login_required
def reading_goals(request):
    goals = ReadingGoal.objects.filter(user=request.user)
    return render(request, 'reading_tracker/goals.html', {'goals': goals})

@login_required
def add_goal(request):
    if request.method == 'POST':
        form = ReadingGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Reading goal added successfully.')
            return redirect('reading_goals')
    else:
        form = ReadingGoalForm()
    return render(request, 'reading_tracker/add_goal.html', {'form': form})

@login_required
def edit_goal(request, pk):
    goal = get_object_or_404(ReadingGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ReadingGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reading goal updated successfully.')
            return redirect('reading_goals')
    else:
        form = ReadingGoalForm(instance=goal)
    return render(request, 'reading_tracker/edit_goal.html', {'form': form, 'goal': goal})

@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(ReadingGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Reading goal deleted successfully.')
        return redirect('reading_goals')
    return render(request, 'reading_tracker/delete_goal.html', {'goal': goal})

@login_required
def reading_progress_data(request):
    # Get reading progress for the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    sessions = ReadingSession.objects.filter(
        user=request.user,
        start_time__gte=thirty_days_ago
    ).order_by('start_time')
    
    dates = []
    pages = []
    
    for session in sessions:
        date_str = session.start_time.strftime('%Y-%m-%d')
        if date_str in dates:
            index = dates.index(date_str)
            pages[index] += session.pages_read
        else:
            dates.append(date_str)
            pages.append(session.pages_read)
    
    return JsonResponse({
        'dates': dates,
        'pages': pages
    })

@login_required
def genre_distribution_data(request):
    # Get genre distribution for user's books
    genres = Book.objects.filter(user=request.user).values('genre').annotate(
        count=Count('genre')
    ).order_by('-count')
    
    return JsonResponse({
        'genres': [genre['genre'] for genre in genres],
        'counts': [genre['count'] for genre in genres]
    })
