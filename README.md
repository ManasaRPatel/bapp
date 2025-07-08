
                                                              Book Reading Habit Analyzer

A web-based application that helps users track, monitor, and analyze their reading habits. Built with Django, this project provides a powerful dashboard for understanding reading patterns, managing goals, and improving consistency.


Features

User Management
- Secure registration and login
- Customizable user profiles
- Privacy controls for reading activity

Book Library
- Add, edit, and delete books
- Track reading status: Currently Reading, Completed, Abandoned
- Upload cover images
- ISBN auto-fill (optional)

Reading Goals
- Set daily, weekly, monthly, or yearly targets
- Visual goal tracking and completion badges
- Motivational streak tracking

Analytics Dashboard
- Reading progress charts
- Genre distribution
- Daily/weekly reading streaks
- Pages read, total time spent reading

Reading Tracker
- Log reading sessions
- Track time, pages, and notes
- Add reflections and session summaries


Tech Stack

Django – Backend Framework
HTML/CSS/JavaScript – Frontend UI
SQLite / PostgreSQL – Database
Chart.js – Analytics and Charts
Bootstrap 5 – Styling
Crispy Forms – Form Styling


Installation

1. Clone the repo:
   git clone https://github.com/your-username/bapp.git
   cd bapp

2. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate
   (On Windows: .\venv\Scripts\activate)

3. Install dependencies:
   pip install -r requirements.txt

4. Run migrations:
   python manage.py migrate

5. Create superuser:
   python manage.py createsuperuser

6. Run the server:
   python manage.py runserver

Then visit: http://127.0.0.1:8000




