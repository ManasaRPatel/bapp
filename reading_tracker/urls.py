from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('api/reading-activity/', views.reading_activity_api, name='reading_activity_api'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # Main pages
    path('', views.dashboard, name='dashboard'),
    path('home/', views.home, name='home'),
    path('progress/', views.reading_progress, name='reading_progress'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('api/genre-distribution/', views.genre_distribution, name='genre_distribution'),
    # Profile management
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Book management
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:pk>/delete/', views.delete_book, name='delete_book'),
    
    # Reading sessions
    path('session/add/', views.add_reading_session, name='add_reading_session'),
    path('session/<int:pk>/edit/', views.edit_session, name='edit_session'),
    path('session/<int:pk>/delete/', views.delete_session, name='delete_session'),
    
    # Reading goals
    path('goals/', views.reading_goals, name='reading_goals'),
    path('goals/add/', views.add_goal, name='add_goal'),
    path('goals/<int:pk>/edit/', views.edit_goal, name='edit_goal'),
    path('goals/<int:pk>/delete/', views.delete_goal, name='delete_goal'),
    
    # API endpoints for charts
    path('api/reading-progress/', views.reading_progress_data, name='reading_progress_data'),
    path('api/book-status/', views.book_status_data, name='book_status_data'),
]