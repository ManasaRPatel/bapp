from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Book(models.Model):
    READING_STATUS = (
        ('CR', 'Currently Reading'),
        ('CO', 'Completed'),
        ('AB', 'Abandoned'),
        ('TB', 'To Be Read')
    )

    GENRE_CHOICES = [
        ('Fiction', (
            ('FIC_LIT', 'Literary Fiction'),
            ('FIC_MYS', 'Mystery'),
            ('FIC_THR', 'Thriller'),
            ('FIC_SFF', 'Science Fiction/Fantasy'),
            ('FIC_ROM', 'Romance'),
            ('FIC_HIS', 'Historical Fiction'),
        )),
        ('Non-Fiction', (
            ('NON_BIO', 'Biography/Memoir'),
            ('NON_HIS', 'History'),
            ('NON_SCI', 'Science'),
            ('NON_TECH', 'Technology'),
            ('NON_SELF', 'Self-Help'),
            ('NON_BUS', 'Business'),
            ('NON_PHIL', 'Philosophy'),
        )),
        ('Other', (
            ('OTH_POET', 'Poetry'),
            ('OTH_DRAMA', 'Drama'),
            ('OTH_COMIC', 'Comics/Graphic Novels'),
            ('OTH_CHILD', 'Children\'s'),
            ('OTH_YA', 'Young Adult'),
            ('OTH_OTHER', 'Other'),
        )),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, blank=True)
    total_pages = models.IntegerField()
    genre = models.CharField(max_length=20, choices=[
        (code, name) for category, subcategories in GENRE_CHOICES 
        for code, name in (subcategories if isinstance(subcategories, tuple) else [(category, subcategories)])
    ])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=READING_STATUS, default='TB')
    cover_image = models.ImageField(upload_to='book_covers', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    def calculate_reading_progress(self):
        """Calculate reading progress and update book status."""
        # Get total pages read from all sessions
        total_pages_read = ReadingSession.objects.filter(book=self).aggregate(
            total_pages=models.Sum('pages_read'))['total_pages'] or 0
        
        # Calculate progress percentage
        progress = min((total_pages_read / self.total_pages) * 100, 100) if self.total_pages > 0 else 0
        
        # Check if this is a new completion
        was_not_completed = self.status != 'CO'
        
        # Update book status based on progress
        if self.status != 'AB':  # Don't update if book is abandoned
            if progress >= 100:
                self.status = 'CO'  # Completed
            elif progress > 0:
                self.status = 'CR'  # Currently Reading
            else:
                self.status = 'TB'  # To Be Read
        
        # Return both progress and whether this was a new completion
        return progress, (was_not_completed and self.status == 'CO')

    def get_genre_display_name(self):
        """Get the display name for the book's genre."""
        for category, subcategories in self.GENRE_CHOICES:
            if isinstance(subcategories, tuple):
                for code, name in subcategories:
                    if code == self.genre:
                        return name
        return self.get_genre_display()

    def save(self, *args, **kwargs):
        if not self.pk:  # New book
            super().save(*args, **kwargs)
        else:
            # Calculate progress and update status before saving
            self.calculate_reading_progress()
            super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class ReadingSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    pages_read = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def duration(self):
        return self.end_time - self.start_time

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update book progress after saving the session
        self.book.calculate_reading_progress()
        self.book.save()

    def __str__(self):
        return f"{self.user.username}'s session - {self.book.title} ({self.pages_read} pages)"

    class Meta:
        ordering = ['-start_time']

class ReadingGoal(models.Model):
    GOAL_TYPES = (
        ('D', 'Daily'),
        ('W', 'Weekly'),
        ('M', 'Monthly'),
        ('Y', 'Yearly')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_type = models.CharField(max_length=1, choices=GOAL_TYPES)
    target_pages = models.IntegerField()
    target_books = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        """Check if the goal is currently active."""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    def get_pages_read_in_period(self):
        """Get total pages read within the goal period."""
        try:
            # Get all reading sessions within the period
            sessions = ReadingSession.objects.filter(
                user=self.user,
                start_time__date__gte=self.start_date,
                start_time__date__lte=self.end_date
            )
            
            # Sum up pages read
            total_pages = sessions.aggregate(
                total=models.Sum('pages_read')
            )['total']
            
            return total_pages or 0
            
        except Exception as e:
            print(f"Error calculating pages read for goal {self.id}: {str(e)}")
            print(f"Goal period: {self.start_date} to {self.end_date}")
            return 0

    def get_books_completed_in_period(self):
        """Get number of books completed within the goal period."""
        try:
            # Get books that were completed within the period
            completed_books = Book.objects.filter(
                user=self.user,
                status='CO',
                readingsession__start_time__date__gte=self.start_date,
                readingsession__start_time__date__lte=self.end_date
            ).distinct()
            
            return completed_books.count()
            
        except Exception as e:
            print(f"Error calculating completed books for goal {self.id}: {str(e)}")
            print(f"Goal period: {self.start_date} to {self.end_date}")
            return 0

    def progress(self):
        """Calculate reading progress for pages within the goal period."""
        try:
            # Validate target pages
            if not self.target_pages or self.target_pages <= 0:
                print(f"Invalid target pages for goal {self.id}: {self.target_pages}")
                return 0
            
            # Get total pages read
            total_pages = self.get_pages_read_in_period()
            print(f"Pages read for goal {self.id}: {total_pages} out of {self.target_pages}")
            
            # Calculate progress percentage
            progress = (total_pages / self.target_pages) * 100
            return min(round(progress, 1), 100)  # Round to 1 decimal and cap at 100%
            
        except Exception as e:
            print(f"Error calculating progress for goal {self.id}: {str(e)}")
            print(f"Target pages: {self.target_pages}")
            return 0

    def books_progress(self):
        """Calculate book completion progress within the goal period."""
        try:
            # Validate target books
            if not self.target_books or self.target_books <= 0:
                return 0
            
            # Get completed books count
            completed_books = self.get_books_completed_in_period()
            
            # Calculate progress percentage
            progress = (completed_books / self.target_books) * 100
            return min(round(progress, 1), 100)  # Round to 1 decimal and cap at 100%
            
        except Exception as e:
            print(f"Error calculating books progress for goal {self.id}: {str(e)}")
            print(f"Target books: {self.target_books}")
            return 0

    def __str__(self):
        return f"{self.user.username}'s {self.get_goal_type_display()} goal"

    class Meta:
        ordering = ['-created_at']

