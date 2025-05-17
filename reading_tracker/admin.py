from django.contrib import admin
from .models import UserProfile, Book, ReadingSession, ReadingGoal

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_public')
    search_fields = ('user__username', 'bio')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'user', 'status', 'created_at')
    list_filter = ('status', 'genre')
    search_fields = ('title', 'author', 'isbn')
    date_hierarchy = 'created_at'

@admin.register(ReadingSession)
class ReadingSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'pages_read', 'start_time', 'end_time')
    list_filter = ('start_time', 'user')
    search_fields = ('book__title', 'notes')
    date_hierarchy = 'start_time'

@admin.register(ReadingGoal)
class ReadingGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal_type', 'target_pages', 'target_books', 'start_date', 'end_date')
    list_filter = ('goal_type', 'start_date')
    search_fields = ('user__username',)
    date_hierarchy = 'start_date'
