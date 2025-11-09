import { ChartOptions, ChartData } from 'chart.js';

// Color palette for consistent chart colors
export const CHART_COLORS = {
  primary: '#3b82f6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  secondary: '#6b7280',
  colors: [
    '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
    '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#14b8a6',
    '#64748b', '#a855f7'
  ]
};

// Category spending pie chart configuration
export const getPieChartConfig = (data: any[]): { data: ChartData<'pie'>, options: ChartOptions<'pie'> } => {
  const labels = data.map(item => item.category);
  const spentData = data.map(item => item.spent);
  const backgroundColors = data.map((_, index) => CHART_COLORS.colors[index % CHART_COLORS.colors.length]);

  return {
    data: {
      labels,
      datasets: [
        {
          data: spentData,
          backgroundColor: backgroundColors,
          borderWidth: 2,
          borderColor: '#ffffff',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right' as const,
          labels: {
            usePointStyle: true,
            padding: 20,
            font: {
              family: 'system-ui, -apple-system, sans-serif',
            },
          },
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const label = context.label || '';
              const value = context.parsed;
              const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
              const percentage = ((value / total) * 100).toFixed(1);
              return `${label}: ₹${value.toLocaleString()} (${percentage}%)`;
            },
          },
        },
      },
    },
  };
};

// Budget utilization bar chart configuration
export const getBarChartConfig = (data: any[]): { data: ChartData<'bar'>, options: ChartOptions<'bar'> } => {
  const labels = data.map(item => item.category);
  const utilizationData = data.map(item => item.utilization);
  
  // Color bars based on utilization percentage
  const backgroundColors = utilizationData.map(utilization => {
    if (utilization >= 100) return CHART_COLORS.danger;    // Over budget - red
    if (utilization >= 80) return CHART_COLORS.warning;    // Close to limit - orange
    return CHART_COLORS.success;                           // Under budget - green
  });

  return {
    data: {
      labels,
      datasets: [
        {
          label: 'Budget Utilization %',
          data: utilizationData,
          backgroundColor: backgroundColors,
          borderColor: backgroundColors.map(color => color + 'dd'),
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              return `Utilization: ${context.parsed.y}%`;
            },
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: (value) => `${value}%`,
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)',
          },
        },
        x: {
          grid: {
            display: false,
          },
        },
      },
    },
  };
};

// Monthly trends line chart configuration (for future use)
export const getLineChartConfig = (): { data: ChartData<'line'>, options: ChartOptions<'line'> } => ({
  data: {
    labels: [],
    datasets: [
      {
        label: 'Monthly Spending',
        data: [],
        borderColor: CHART_COLORS.primary,
        backgroundColor: CHART_COLORS.primary + '20',
        tension: 0.4,
        fill: true,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value) => `₹${value}`,
        },
      },
    },
  },
});