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

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Pages Read',
                data: data.pages,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Pages'
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
}); 