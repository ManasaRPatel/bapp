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

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, blank=True)
    total_pages = models.IntegerField()
    genre = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=READING_STATUS, default='TB')
    cover_image = models.ImageField(upload_to='book_covers', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

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
        return self.start_date <= timezone.now().date() <= self.end_date

    def progress(self):
        if self.goal_type == 'D':
            sessions = ReadingSession.objects.filter(
                user=self.user,
                start_time__date=timezone.now().date()
            )
        elif self.goal_type == 'W':
            sessions = ReadingSession.objects.filter(
                user=self.user,
                start_time__week=timezone.now().isocalendar()[1],
                start_time__year=timezone.now().year
            )
        elif self.goal_type == 'M':
            sessions = ReadingSession.objects.filter(
                user=self.user,
                start_time__month=timezone.now().month,
                start_time__year=timezone.now().year
            )
        else:  # Yearly
            sessions = ReadingSession.objects.filter(
                user=self.user,
                start_time__year=timezone.now().year
            )
        
        total_pages = sessions.aggregate(models.Sum('pages_read'))['pages_read__sum'] or 0
        return (total_pages / self.target_pages) * 100 if self.target_pages > 0 else 0

    def __str__(self):
        return f"{self.user.username}'s {self.get_goal_type_display()} goal"

    class Meta:
        ordering = ['-created_at']
