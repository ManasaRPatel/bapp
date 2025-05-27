from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        next_page='/'
    ), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # Main pages
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Profile management
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # API endpoints for charts
    path('api/genre-distribution/', views.genre_distribution, name='genre_distribution'),
    path('api/book-status/', views.book_status_data, name='book_status_data'),
    
    # Book management
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:pk>/delete/', views.delete_book, name='delete_book'),
    path('books/<int:pk>/complete/', views.mark_book_completed, name='mark_book_completed'),
    
    # Reading sessions
    path('books/<int:book_id>/add-session/', views.add_reading_session, name='add_reading_session'),
    path('sessions/<int:pk>/', views.session_detail, name='session_detail'),
    path('sessions/<int:pk>/edit/', views.edit_session, name='edit_session'),
    path('sessions/<int:pk>/delete/', views.delete_session, name='delete_session'),
    
    # Reading goals
    path('goals/', views.reading_goals, name='reading_goals'),
    path('goals/add/', views.add_goal, name='add_goal'),
    path('goals/<int:pk>/edit/', views.edit_goal, name='edit_goal'),
    path('goals/<int:pk>/delete/', views.delete_goal, name='delete_goal'),
]