/**
 * Radar Chart Visualization with Dynamic Gradient Coloring
 * Renders a Chart.js radar chart comparing student metrics to cohort averages
 * The polygon fill color is dynamic based on the "worst" metric to highlight areas of concern.
 * 
 * Expects global variable: window.chartData with structure:
 * {
 *   student: { stress, sleep, grades, attendance },
 *   cohort: { stress, sleep, grades, attendance }
 * }
 */

/**
 * Get color based on value (0-100 scale)
 * For most metrics: low = red (bad), high = green (good)
 * For stress: inverted because high stress is bad
 */
function getColorForValue(value, metricIndex) {
    // Stress is at index 0 and should be inverted (high stress = bad)
    const isStress = metricIndex === 0;
    const effectiveValue = isStress ? (100 - value) : value;

    // Red (concern) -> Yellow (warning) -> Green (good)
    if (effectiveValue < 40) {
        // Red zone
        const ratio = effectiveValue / 40;
        return `rgba(${220 + (35 * ratio)}, ${20 + (60 * ratio)}, 20, 1)`;
    } else if (effectiveValue < 70) {
        // Yellow zone
        const ratio = (effectiveValue - 40) / 30;
        return `rgba(255, ${80 + (175 * ratio)}, 20, 1)`;
    } else {
        // Green zone
        const ratio = (effectiveValue - 70) / 30;
        return `rgba(${150 - (70 * ratio)}, ${200 + (55 * ratio)}, ${50 + (150 * ratio)}, 1)`;
    }
}

/**
 * Get base RGB values for a score (0-100 normalized health score)
 */
function getBaseColor(score) {
    if (score < 40) return [220, 53, 69]; // Red
    if (score < 70) return [255, 193, 7]; // Yellow
    return [40, 167, 69]; // Green
}

function initRadarChart(canvasId, labelText) {
    const ctx = document.getElementById(canvasId);

    if (!ctx || !window.chartData) {
        console.error('Chart canvas or data not found');
        return;
    }

    const studentData = [
        window.chartData.student.stress,
        window.chartData.student.sleep,
        window.chartData.student.grades,
        window.chartData.student.attendance
    ];

    // Calculate "Health Scores" for each metric (higher is better)
    const healthScores = studentData.map((val, idx) => idx === 0 ? (100 - val) : val);

    // Find the WORST score to determine the overall chart color (highlight concern)
    const minScore = Math.min(...healthScores);
    const [r, g, b] = getBaseColor(minScore);

    // Generate dynamic colors for each point
    const pointColors = studentData.map((value, index) => getColorForValue(value, index));

    const data = {
        labels: ['Stress', 'Sleep', 'Grades', 'Attendance'],
        datasets: [
            {
                label: labelText || 'Student',
                data: studentData,
                fill: true,
                backgroundColor: function (context) {
                    const ctx = context.chart.ctx;
                    const chartArea = context.chart.chartArea;
                    if (!chartArea) return null;

                    // Create a radial gradient for the polygon fill
                    // Center is opaque, edges fade out
                    const centerX = (chartArea.left + chartArea.right) / 2;
                    const centerY = (chartArea.top + chartArea.bottom) / 2;
                    const maxRadius = Math.min(chartArea.right - chartArea.left, chartArea.bottom - chartArea.top) / 2;

                    const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, maxRadius);
                    gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, 0.5)`);   // Center: stronger color
                    gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0.1)`);   // Edge: lighter

                    return gradient;
                },
                borderColor: `rgb(${r}, ${g}, ${b})`,
                pointBackgroundColor: pointColors,
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: pointColors,
                pointRadius: 6,
                pointHoverRadius: 8,
                borderWidth: 3
            },
            {
                label: 'Cohort Average',
                data: [
                    window.chartData.cohort.stress,
                    window.chartData.cohort.sleep,
                    window.chartData.cohort.grades,
                    window.chartData.cohort.attendance
                ],
                fill: false,
                backgroundColor: 'rgba(200, 200, 200, 0.1)',
                borderColor: 'rgb(150, 150, 150)',
                borderDash: [5, 5],
                pointBackgroundColor: 'rgb(150, 150, 150)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(150, 150, 150)',
                pointRadius: 4,
                borderWidth: 2
            }
        ]
    };

    const config = {
        type: 'radar',
        data: data,
        options: {
            elements: {
                line: {
                    borderWidth: 3
                }
            },
            scales: {
                r: {
                    angleLines: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    pointLabels: {
                        font: {
                            size: 14,
                            weight: '500'
                        }
                    },
                    ticks: {
                        beginAtZero: true,
                        max: 100,
                        stepSize: 20,
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 15,
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            let value = context.parsed.r;
                            let metric = context.label;

                            // Convert normalized values back to actual values
                            let actualValue;
                            if (metric === 'Stress') {
                                // Stress is now direct: (stress / 5) * 100
                                actualValue = ((value / 100) * 5).toFixed(1);
                                return label + ': ' + actualValue + '/5';
                            } else if (metric === 'Sleep') {
                                // Sleep was: (hours / 8) * 100
                                actualValue = ((value / 100) * 8).toFixed(2);
                                return label + ': ' + actualValue + ' hours';
                            } else if (metric === 'Grades' || metric === 'Attendance') {
                                return label + ': ' + value.toFixed(1) + '%';
                            }
                            return label + ': ' + value;
                        }
                    }
                }
            }
        }
    };

    new Chart(ctx, config);
}
