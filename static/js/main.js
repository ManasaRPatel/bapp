// Chart.js default configuration
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
Chart.defaults.color = '#666';

// Utility function to format dates
function formatDate(date) {
    return new Date(date).toLocaleDateString();
}

// Initialize reading progress chart
function initReadingProgressChart(elementId, data) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;

    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(0, 123, 255, 0.4)');
    gradient.addColorStop(1, 'rgba(0, 123, 255, 0.0)');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Pages Read (Log Scale)',
                data: data.log_pages,
                borderColor: '#007bff',
                backgroundColor: gradient,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#007bff',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2
            }, {
                label: 'Actual Pages Read',
                data: data.pages,
                borderColor: '#28a745',
                backgroundColor: 'transparent',
                fill: false,
                tension: 0.4,
                pointRadius: 2,
                pointHoverRadius: 4,
                hidden: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#007bff',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            const datasetLabel = context.dataset.label;
                            const value = context.raw;
                            if (datasetLabel.includes('Log')) {
                                return `${datasetLabel}: ${value.toFixed(2)}`;
                            }
                            return `${datasetLabel}: ${value} pages`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Reading Progress',
                        font: {
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Date',
                        font: {
                            weight: 'bold'
                        }
                    }
                }
            }
        }
    });
}

// Initialize genre distribution chart
function initGenreChart(elementId, data) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.genres,
            datasets: [{
                data: data.counts,
                backgroundColor: [
                    '#007bff',
                    '#28a745',
                    '#dc3545',
                    '#ffc107',
                    '#17a2b8',
                    '#6610f2'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

// Reading session timer
class ReadingTimer {
    constructor() {
        this.startTime = null;
        this.timerInterval = null;
    }

    start() {
        this.startTime = new Date();
        this.updateDisplay();
        this.timerInterval = setInterval(() => this.updateDisplay(), 1000);
    }

    stop() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        return this.getSessionDuration();
    }

    updateDisplay() {
        if (!this.startTime) return;
        
        const now = new Date();
        const duration = Math.floor((now - this.startTime) / 1000);
        const hours = Math.floor(duration / 3600);
        const minutes = Math.floor((duration % 3600) / 60);
        const seconds = duration % 60;
        
        const display = document.getElementById('reading-timer');
        if (display) {
            display.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    getSessionDuration() {
        if (!this.startTime) return 0;
        return Math.floor((new Date() - this.startTime) / 1000);
    }
}

// Initialize reading timer
const readingTimer = new ReadingTimer();

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));

    // Reading session controls
    const startButton = document.getElementById('start-reading');
    const stopButton = document.getElementById('stop-reading');
    
    if (startButton) {
        startButton.addEventListener('click', () => {
            readingTimer.start();
            startButton.style.display = 'none';
            stopButton.style.display = 'block';
        });
    }
    
    if (stopButton) {
        stopButton.addEventListener('click', () => {
            const duration = readingTimer.stop();
            document.getElementById('session-duration').value = duration;
            startButton.style.display = 'block';
            stopButton.style.display = 'none';
        });
    }

    // Add event listener for reading session form
    const readingSessionForm = document.getElementById('reading-session-form');
    if (readingSessionForm) {
        readingSessionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
        });
    }
});

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 