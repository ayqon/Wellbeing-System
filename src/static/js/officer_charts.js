document.addEventListener('DOMContentLoaded', function () {
    if (!window.officerData) return;

    const data = window.officerData;
    const ctx = document.getElementById('dynamicChart').getContext('2d');
    let chart = null;

    // DOM Elements
    const xSelect = document.getElementById('xAxisSelect');
    const ySelect = document.getElementById('yAxisSelect');
    const clusterSelect = document.getElementById('clusterSelect');
    const clusterToggles = document.getElementById('clusterToggles');

    // Configuration: 5 Clusters per metric
    const clusters = {
        grade: [
            { label: 'Fail (<40)', min: 0, max: 39.9, color: '#ef4444' },
            { label: 'Pass (40-49)', min: 40, max: 49.9, color: '#f97316' },
            { label: '2:2 (50-59)', min: 50, max: 59.9, color: '#eab308' },
            { label: '2:1 (60-69)', min: 60, max: 69.9, color: '#84cc16' },
            { label: 'First (70+)', min: 70, max: 100, color: '#22c55e' }
        ],
        attendance: [
            { label: 'Critical (<60)', min: 0, max: 59.9, color: '#ef4444' },
            { label: 'Poor (60-74)', min: 60, max: 74.9, color: '#f97316' },
            { label: 'Warning (75-84)', min: 75, max: 84.9, color: '#eab308' },
            { label: 'Good (85-94)', min: 85, max: 94.9, color: '#84cc16' },
            { label: 'Excellent (95+)', min: 95, max: 100, color: '#22c55e' }
        ],
        sleep: [
            { label: 'Very Low (<4)', min: 0, max: 3.9, color: '#ef4444' },
            { label: 'Low (4-5.9)', min: 4, max: 5.9, color: '#f97316' },
            { label: 'Optimal (6-8.9)', min: 6, max: 8.9, color: '#22c55e' },
            { label: 'High (9-10.9)', min: 9, max: 10.9, color: '#3b82f6' },
            { label: 'Excessive (11+)', min: 11, max: 24, color: '#6366f1' }
        ],
        stress: [
            { label: 'Very Low (1)', min: 0, max: 1.5, color: '#22c55e' },
            { label: 'Low (2)', min: 1.51, max: 2.5, color: '#84cc16' },
            { label: 'Moderate (3)', min: 2.51, max: 3.5, color: '#eab308' },
            { label: 'High (4)', min: 3.51, max: 4.5, color: '#f97316' },
            { label: 'Very High (5)', min: 4.51, max: 5, color: '#ef4444' }
        ]
    };

    // State
    let activeClusters = new Set(); // Stores indices of active clusters

    function init() {
        // Initial render
        updateToggles();
        renderChart();

        // Event Listeners
        xSelect.addEventListener('change', () => { renderChart(); });
        ySelect.addEventListener('change', () => { renderChart(); });
        clusterSelect.addEventListener('change', () => {
            updateToggles();
            renderChart();
        });
    }

    function updateToggles() {
        clusterToggles.innerHTML = '';
        activeClusters.clear();

        const mode = clusterSelect.value;
        if (mode === 'none') return;

        const config = clusters[mode];
        config.forEach((c, index) => {
            activeClusters.add(index); // Enable all by default

            const wrapper = document.createElement('div');
            wrapper.className = 'checkbox-wrapper gap-2';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = true;
            checkbox.dataset.index = index;
            checkbox.addEventListener('change', (e) => {
                if (e.target.checked) activeClusters.add(index);
                else activeClusters.delete(index);
                renderChart();
            });

            const label = document.createElement('label');
            label.textContent = c.label;
            label.style.color = c.color;
            label.style.marginBottom = '0';
            label.style.cursor = 'pointer';
            label.addEventListener('click', () => checkbox.click());

            wrapper.appendChild(checkbox);
            wrapper.appendChild(label);
            clusterToggles.appendChild(wrapper);
        });
    }

    function getMetricValue(student, metric) {
        switch (metric) {
            case 'grade': return student.grade || 0;
            case 'attendance': return student.attendance || 0;
            case 'sleep': return student.sleep || 0;
            case 'stress': return student.stress || 0;
            default: return 0;
        }
    }

    function getClusterIndex(student, mode) {
        if (mode === 'none') return -1;
        const val = getMetricValue(student, mode);
        const config = clusters[mode];
        return config.findIndex(c => val >= c.min && val <= c.max);
    }

    function renderChart() {
        const xMetric = xSelect.value;
        const yMetric = ySelect.value;
        const clusterMode = clusterSelect.value;

        // Prepare Datasets
        let datasets = [];

        if (clusterMode === 'none') {
            datasets.push({
                label: 'All Students',
                data: data.map(s => ({
                    x: getMetricValue(s, xMetric),
                    y: getMetricValue(s, yMetric),
                    student: s
                })),
                backgroundColor: 'rgba(59, 130, 246, 0.6)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 1
            });
        } else {
            const config = clusters[clusterMode];
            config.forEach((c, index) => {
                if (!activeClusters.has(index)) return;

                const clusterData = data.filter(s => getClusterIndex(s, clusterMode) === index);

                datasets.push({
                    label: c.label,
                    data: clusterData.map(s => ({
                        x: getMetricValue(s, xMetric),
                        y: getMetricValue(s, yMetric),
                        student: s
                    })),
                    backgroundColor: c.color,
                    borderColor: c.color,
                    borderWidth: 1
                });
            });
        }

        if (chart) chart.destroy();

        chart = new Chart(ctx, {
            type: 'scatter',
            data: { datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: { display: true, text: xSelect.options[xSelect.selectedIndex].text },
                        beginAtZero: true
                    },
                    y: {
                        title: { display: true, text: ySelect.options[ySelect.selectedIndex].text },
                        beginAtZero: true
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const pt = context.raw;
                                return `${pt.student.username}: ${pt.x}, ${pt.y}`;
                            }
                        }
                    }
                }
            }
        });
    }

    init();
});
