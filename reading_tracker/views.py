from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Book, ReadingSession, ReadingGoal, UserProfile
from .forms import (UserRegistrationForm, UserProfileForm, BookForm,
                   ReadingSessionForm, ReadingGoalForm)
import math
from django.urls import reverse

def home(request):
    return render(request, 'reading_tracker/welcome.html')


# ...existing code...

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a UserProfile for the new user
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
# ...existing code...

@login_required
def dashboard(request):
    try:
        # Get user's reading statistics
        total_books = Book.objects.filter(user=request.user).count()
        books_completed = Book.objects.filter(user=request.user, status='CO').count()
        
        # Calculate total pages read
        total_pages = ReadingSession.objects.filter(user=request.user).aggregate(
            total=Sum('pages_read'))['total'] or 0
        
        # Get currently reading book with progress
        current_book = Book.objects.filter(user=request.user, status='CR').first()
        if current_book:
            # Calculate reading progress
            pages_read = ReadingSession.objects.filter(
                book=current_book
            ).aggregate(total=Sum('pages_read'))['total'] or 0
            
            current_book.pages_read = pages_read
            current_book.progress = round((pages_read / current_book.total_pages) * 100) if current_book.total_pages > 0 else 0
        
        # Debug: Print all goals for this user
        all_goals = ReadingGoal.objects.filter(user=request.user)
        print("\nAll goals for user:")
        for goal in all_goals:
            print(f"Goal ID: {goal.id}")
            print(f"Period: {goal.start_date} to {goal.end_date}")
            print(f"Target Pages: {goal.target_pages}")
            print(f"Target Books: {goal.target_books}")
            print(f"Created At: {goal.created_at}")
            print("---")
        
        # Get active reading goal - get the most recent one that's currently active
        today = timezone.now().date()
        print(f"\nToday's date: {today}")
        
        active_goals = ReadingGoal.objects.filter(
            user=request.user,
            start_date__lte=today,
            end_date__gte=today
        )
        
        print("\nActive goals found:")
        for goal in active_goals:
            print(f"Goal ID: {goal.id}")
            print(f"Period: {goal.start_date} to {goal.end_date}")
        
        active_goal = active_goals.order_by('-created_at').first()
        
        print("\nSelected active goal:")
        if active_goal:
            print(f"Goal ID: {active_goal.id}")
            print(f"Period: {active_goal.start_date} to {active_goal.end_date}")
            print(f"Target Pages: {active_goal.target_pages}")
            print(f"Target Books: {active_goal.target_books}")

            try:
                # Calculate days remaining
                days_remaining = (active_goal.end_date - today).days
                
                # Get pages and books read in the goal period
                pages_read_in_period = active_goal.get_pages_read_in_period()
                books_completed_in_period = active_goal.get_books_completed_in_period()
                
                print(f"\nProgress calculations:")
                print(f"Days remaining: {days_remaining}")
                print(f"Pages read in period: {pages_read_in_period}")
                print(f"Books completed in period: {books_completed_in_period}")
                
                # Calculate remaining targets
                pages_remaining = max(0, active_goal.target_pages - pages_read_in_period)
                books_remaining = max(0, active_goal.target_books - books_completed_in_period) if active_goal.target_books else 0
                
                # Calculate daily targets needed
                pages_needed_per_day = math.ceil(pages_remaining / days_remaining) if days_remaining > 0 else 0
                
                # Calculate progress percentages
                pages_progress = (pages_read_in_period / active_goal.target_pages * 100) if active_goal.target_pages > 0 else 0
                books_progress = (books_completed_in_period / active_goal.target_books * 100) if active_goal.target_books > 0 else 0
                
                print(f"Pages progress: {pages_progress}%")
                print(f"Books progress: {books_progress}%")
                
                # Add goal progress information
                active_goal.days_remaining = days_remaining
                active_goal.pages_read = pages_read_in_period
                active_goal.pages_remaining = pages_remaining
                active_goal.pages_needed_per_day = pages_needed_per_day
                active_goal.books_completed = books_completed_in_period
                active_goal.books_remaining = books_remaining
                active_goal.progress = min(round(pages_progress, 1), 100)
                active_goal.books_progress = min(round(books_progress, 1), 100)
                
            except Exception as e:
                print(f"\nGoal Progress Error: {str(e)}")
                print(f"Goal ID: {active_goal.id}")
                print(f"Goal Period: {active_goal.start_date} to {active_goal.end_date}")
                print(f"Target Pages: {active_goal.target_pages}")
                print(f"Target Books: {active_goal.target_books}")
                messages.error(request, "There was an error calculating goal progress. Please check your goal settings.")
                active_goal = None
        else:
            print("No active goal found")
        
        context = {
            'total_books': total_books,
            'books_completed': books_completed,
            'total_pages': total_pages,
            'active_goal': active_goal,
            'current_book': current_book
        }
        
        print("\nContext being sent to template:")
        print(f"Active goal in context: {'Yes' if active_goal else 'No'}")
        
        return render(request, 'reading_tracker/dashboard.html', context)
        
    except Exception as e:
        print(f"\nDashboard Error: {str(e)}")
        messages.error(request, "There was an error loading the dashboard. Please try again.")
        context = {
            'total_books': 0,
            'books_completed': 0,
            'total_pages': 0,
            'active_goal': None,
            'current_book': None
        }
        return render(request, 'reading_tracker/dashboard.html', context)

@login_required
def profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    books = Book.objects.filter(user=request.user)
    reading_sessions = ReadingSession.objects.filter(user=request.user).order_by('-start_time')
    
    # Calculate reading statistics
    total_books = books.count()
    books_completed = books.filter(status='CO').count()
    total_pages_read = reading_sessions.aggregate(total=Sum('pages_read'))['total'] or 0
    
    # Prepare reading progress data for the chart
    last_30_days = reading_sessions.filter(
        start_time__gte=timezone.now() - timezone.timedelta(days=30)
    ).values('start_time__date').annotate(
        pages=Sum('pages_read')
    ).order_by('start_time__date')
    
    chart_data = {
        'dates': [session['start_time__date'].strftime('%Y-%m-%d') for session in last_30_days],
        'pages': [session['pages'] for session in last_30_days]
    }
    
    # Get active reading goals
    active_goals = ReadingGoal.objects.filter(
        user=request.user,
        end_date__gte=timezone.now().date()
    )
    
    return render(request, 'reading_tracker/profile.html', {
        'profile': user_profile,
        'total_books': total_books,
        'books_completed': books_completed,
        'pages_read': total_pages_read,
        'chart_data': chart_data,
        'active_goals': active_goals
    })

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
    
    # Calculate reading progress
    total_pages_read = sessions.aggregate(Sum('pages_read'))['pages_read__sum'] or 0
    reading_progress = (total_pages_read / book.total_pages) * 100 if book.total_pages > 0 else 0
    
    # Get reading sessions data for the chart
    sessions_data = list(sessions.values('start_time', 'pages_read'))
    chart_data = {
        'dates': [session['start_time'].strftime('%Y-%m-%d') for session in sessions_data],
        'pages': [session['pages_read'] for session in sessions_data]
    }
    
    return render(request, 'reading_tracker/book_detail.html', {
        'book': book,
        'sessions': sessions,
        'reading_progress': reading_progress,
        'pages_read': total_pages_read,
        'chart_data': chart_data,
        'just_completed': request.GET.get('just_completed') == 'true'
    })

@login_required
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            # Check if the book was completed
            old_status = book.status
            book = form.save(commit=False)
            just_completed = old_status != 'CO' and book.status == 'CO'
            book.save()
            
            messages.success(request, 'Book updated successfully.')
            if just_completed:
                return redirect(f'/books/{pk}/?just_completed=true')
            return redirect('book_detail', pk=pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'reading_tracker/edit_book.html', {'form': form, 'book': book})

@login_required
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk, user=request.user)
    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f'"{book_title}" has been deleted successfully.')
        
        # Return JSON response if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'"{book_title}" has been deleted successfully.',
                'redirect_url': reverse('book_list')
            })
        
        # For regular requests, redirect to book list
        return redirect('book_list')
    
    # GET request - show confirmation page
    return render(request, 'reading_tracker/delete_book.html', {'book': book})

@login_required
def add_reading_session(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)
    
    if request.method == 'POST':
        form = ReadingSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user
            session.book = book
            
            # Validate pages read against book's total pages
            total_pages_read = ReadingSession.objects.filter(book=book).aggregate(
                total=Sum('pages_read'))['total'] or 0
            if total_pages_read + session.pages_read > book.total_pages:
                form.add_error('pages_read', 
                    f'Total pages read would exceed book\'s total pages ({book.total_pages})')
            else:
                session.save()
                
                # Update book progress and status
                progress, just_completed = book.calculate_reading_progress()
                book.save()
                
                messages.success(request, 'Reading session added successfully.')
                if just_completed:
                    return redirect(f'/books/{book_id}/?just_completed=true')
                return redirect('book_detail', pk=book_id)
    else:
        # Pre-fill the start time with current time
        form = ReadingSessionForm(initial={
            'start_time': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        })
    
    return render(request, 'reading_tracker/add_reading_session.html', {
        'form': form,
        'book': book
    })

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
def reading_progress(request):
    return render(request, 'reading_tracker/reading_progress.html')

@login_required
def reading_progress_data(request):
    """API endpoint for reading progress charts"""
    days = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Get daily pages read
    daily_pages = ReadingSession.objects.filter(
        user=request.user,
        start_time__date__gte=start_date
    ).values('start_time__date').annotate(
        pages=Sum('pages_read')
    ).order_by('start_time__date')
    
    # Fill in missing dates with 0 pages
    dates = []
    daily_values = []
    total_pages = 0
    
    current_date = start_date
    daily_data = {item['start_time__date']: item['pages'] for item in daily_pages}
    
    while current_date <= timezone.now().date():
        dates.append(current_date.strftime('%Y-%m-%d'))
        pages = daily_data.get(current_date, 0)
        daily_values.append(pages)
        total_pages += pages
        current_date += timedelta(days=1)
    
    # Calculate average pages per day
    avg_pages = round(total_pages / len(dates), 1) if dates else 0
    
    return JsonResponse({
        'dates': dates,
        'daily_pages': daily_values,
        'total_pages': total_pages,
        'avg_pages_per_day': avg_pages
    })

@login_required
def book_status_data(request):
    """API endpoint for book status chart"""
    status_counts = Book.objects.filter(user=request.user).values('status').annotate(
        count=Count('status')
    )
    
    # Initialize all possible statuses with 0
    data = {
        'labels': ['Completed', 'Currently Reading', 'Abandoned'],
        'counts': [0, 0, 0],
        'colors': ['#4BC0C0', '#FF9F40', '#FF6384']  # Green, Orange, Red
    }
    
    # Map database status codes to array indices
    status_map = {
        'CO': 0,  # Completed
        'CR': 1,  # Currently Reading
        'AB': 2   # Abandoned
    }
    
    # Fill in actual counts
    for status in status_counts:
        if status['status'] in status_map:
            data['counts'][status_map[status['status']]] = status['count']
    
    return JsonResponse(data)

@login_required
def genre_distribution(request):
    """API endpoint for genre distribution chart"""
    books = Book.objects.filter(user=request.user)
    
    # Get genre counts
    genre_stats = books.values('genre').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Prepare data for chart
    genres = []
    counts = []
    colors = ['#36A2EB', '#4BC0C0', '#FF9F40', '#FF6384', '#9966FF', '#FFCD56']
    
    for i, stat in enumerate(genre_stats):
        genre_name = dict(Book._meta.get_field('genre').choices)[stat['genre']]
        genres.append(genre_name)
        counts.append(stat['count'])
    
    return JsonResponse({
        'labels': genres,
        'data': counts,
        'colors': colors[:len(genres)]
    })

@login_required
def analytics_dashboard(request):
    # Time range for analysis
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Get reading sessions for the period
    sessions = ReadingSession.objects.filter(
        user=request.user,
        start_time__gte=start_date
    )
    
    # Daily pages read
    daily_pages = sessions.values('start_time__date').annotate(
        pages=Sum('pages_read')
    ).order_by('start_time__date')
    
    # Reading patterns
    time_patterns = sessions.annotate(
        hour=ExtractHour('start_time')
    ).values('hour').annotate(
        count=Count('id'),
        avg_pages=Avg('pages_read')
    ).order_by('hour')
    
    weekday_patterns = sessions.annotate(
        weekday=ExtractWeekDay('start_time')
    ).values('weekday').annotate(
        count=Count('id'),
        avg_pages=Avg('pages_read')
    ).order_by('weekday')
    
    # Genre analysis
    genre_stats = Book.objects.filter(
        user=request.user,
        readingsession_start_time_gte=start_date
    ).values('genre').annotate(
        total_pages=Sum('readingsession__pages_read'),
        total_time=Sum('readingsession_end_time') - Sum('readingsession_start_time'),
        book_count=Count('id', distinct=True)
    ).order_by('-total_pages')
    
    # Reading streaks
    streak_data = {}
    for session in sessions:
        date_str = session.start_time.date().isoformat()
        if date_str in streak_data:
            streak_data[date_str] += session.pages_read
        else:
            streak_data[date_str] = session.pages_read
    
    # Mood and comprehension analysis
    mood_stats = sessions.exclude(mood='').values('mood').annotate(
        count=Count('id'),
        avg_pages=Avg('pages_read')
    ).order_by('mood')
    
    comprehension_stats = sessions.exclude(comprehension='').values('comprehension').annotate(
        count=Count('id'),
        avg_pages=Avg('pages_read')
    ).order_by('comprehension')
    
    # Calculate total statistics
    total_stats = {
        'total_books': Book.objects.filter(user=request.user, status='CO').count(),
        'total_pages': sessions.aggregate(Sum('pages_read'))['pages_read__sum'] or 0,
        'total_time': sum((s.duration().total_seconds() / 3600) for s in sessions),
        'avg_pages_per_session': sessions.aggregate(Avg('pages_read'))['pages_read__avg'] or 0,
        'total_sessions': sessions.count(),
    }
    
    context = {
        'total_stats': total_stats,
        'daily_pages': list(daily_pages),
        'time_patterns': list(time_patterns),
        'weekday_patterns': list(weekday_patterns),
        'genre_stats': list(genre_stats),
        'streak_data': streak_data,
        'mood_stats': list(mood_stats),
        'comprehension_stats': list(comprehension_stats),
        'days': days,
    }
    
    return render(request, 'reading_tracker/analytics.html', context)

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

@login_required
def reading_activity_data(request):
    """API endpoint for reading activity heatmap"""
    try:
        # Get data for the last 365 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365)
        
        # Get daily reading activity
        daily_activity = ReadingSession.objects.filter(
            user=request.user,
            start_time__date__gte=start_date
        ).values('start_time__date').annotate(
            pages=Sum('pages_read')
        )
        
        # Convert to the format expected by Cal-Heatmap
        activity_data = {}
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        last_active_date = None
        
        # Process all dates in range
        current_date = start_date
        while current_date <= end_date:
            # Find pages read for this date
            date_activity = next(
                (item for item in daily_activity if item['start_time__date'] == current_date),
                None
            )
            pages = date_activity['pages'] if date_activity else 0
            
            # Add to activity data if there was reading activity
            if pages > 0:
                # Convert date to Unix timestamp (seconds since epoch)
                timestamp = int(datetime.combine(current_date, datetime.min.time()).timestamp())
                activity_data[str(timestamp)] = pages
                
                # Update streak information
                if last_active_date is None or (current_date - last_active_date).days == 1:
                    temp_streak += 1
                else:
                    temp_streak = 1
                
                if temp_streak > longest_streak:
                    longest_streak = temp_streak
                
                last_active_date = current_date
                
                # Update current streak if it includes today
                if current_date == end_date:
                    current_streak = temp_streak
            else:
                if current_date == end_date and last_active_date == current_date - timedelta(days=1):
                    current_streak = temp_streak
                temp_streak = 0
            
            current_date += timedelta(days=1)
        
        print("Activity Data:", activity_data)  # Debug print
        
        return JsonResponse({
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'data': activity_data
        })
    except Exception as e:
        print(f"Reading Activity Error: {str(e)}")  # Debug print
        return JsonResponse({
            'current_streak': 0,
            'longest_streak': 0,
            'data': {}
        })

@login_required
def mark_book_completed(request, pk):
    book = get_object_or_404(Book, pk=pk, user=request.user)
    if request.method == 'POST':
        # Update book status to completed
        book.status = 'CO'
        book.save()
        
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'book_title': book.title,
                'redirect_url': reverse('dashboard'),
                'status': 'CO'
            })
        
        # For regular requests, redirect to book detail with completion flag
        messages.success(request, f'"{book.title}" has been marked as completed!')
        return redirect(f'/books/{pk}/?just_completed=true')
    
    # GET request - show confirmation page
    return render(request, 'reading_tracker/mark_book_completed.html', {'book': book})
