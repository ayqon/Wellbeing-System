document.addEventListener('DOMContentLoaded', function () {
    if (!window.academicChartsData) return;

    const data = window.academicChartsData;

    // Common Chart.js options
    const commonOptions = {
        responsive: true,
        plugins: {
            legend: {
                display: false
            }
        }
    };

    // 1. Scatter Plot: Grades vs Attendance
    const scatterCtx = document.getElementById('scatterChart').getContext('2d');
    new Chart(scatterCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Student Performance',
                data: data.scatter, // [{x: attendance, y: grade, name: ...}]
                backgroundColor: 'rgba(59, 130, 246, 0.6)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 1
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Attendance (%)'
                    },
                    min: 0,
                    max: 100
                },
                y: {
                    title: {
                        display: true,
                        text: 'Grade (%)'
                    },
                    min: 0,
                    max: 100
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const point = context.raw;
                            return `${point.name}: Attendance ${point.x}%, Grade ${point.y}%`;
                        }
                    }
                }
            }
        }
    });

    // 2. Histogram (Bar Chart): Average Grade per Module
    const histogramCtx = document.getElementById('histogramChart').getContext('2d');
    new Chart(histogramCtx, {
        type: 'bar',
        data: {
            labels: data.histogram.map(item => item.label),
            datasets: [{
                label: 'Average Grade',
                data: data.histogram.map(item => item.value),
                backgroundColor: 'rgba(16, 185, 129, 0.6)',
                borderColor: 'rgba(16, 185, 129, 1)',
                borderWidth: 1
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Average Grade (%)'
                    }
                }
            }
        }
    });
});
