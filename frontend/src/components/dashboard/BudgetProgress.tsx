import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { getBarChartConfig } from '../../utils/chartConfig';
import type { CategorySpending } from '../../types';

// Register Chart.js components we need for bar chart
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

// Props for budget progress component
interface BudgetProgressProps {
  data: CategorySpending[];
  className?: string;
}

export const BudgetProgress: React.FC<BudgetProgressProps> = ({ 
  data, 
  className = '' 
}) => {
  // Filter out categories with no budget set
  const filteredData = data.filter(item => item.budget > 0);
  
  // Get chart configuration based on data
  const chartConfig = getBarChartConfig(filteredData);

  // Count categories that are over budget
  const overBudgetCount = filteredData.filter(item => item.utilization >= 100).length;

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
      {/* Chart header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Budget Utilization
          </h3>
          <p className="text-sm text-gray-500">
            {overBudgetCount > 0 
              ? `${overBudgetCount} categor${overBudgetCount === 1 ? 'y' : 'ies'} over budget`
              : 'All categories within budget'
            }
          </p>
        </div>
        
        {/* Legend for color coding */}
        <div className="flex items-center space-x-4 text-xs">
          <div className="flex items-center">
            <div className="w-3 h-3 mr-1 bg-green-500 rounded"></div>
            <span>Under 80%</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 mr-1 bg-yellow-500 rounded"></div>
            <span>80-100%</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 mr-1 bg-red-500 rounded"></div>
            <span>Over budget</span>
          </div>
        </div>
      </div>

      {/* Chart container */}
      <div className="h-80">
        {filteredData.length > 0 ? (
          // Render bar chart if we have data
          <Bar data={chartConfig.data} options={chartConfig.options} />
        ) : (
          // Show empty state if no data
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <div className="mb-2 text-4xl">💰</div>
              <p>No budget data available</p>
              <p className="text-sm">Set category budgets to track utilization</p>
            </div>
          </div>
        )}
      </div>

      {/* Budget status summary */}
      {filteredData.length > 0 && (
        <div className="pt-4 mt-4 border-t border-gray-200">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="text-center">
              <div className="font-semibold text-green-600">
                {filteredData.filter(item => item.utilization < 80).length}
              </div>
              <div className="text-gray-600">Good</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-yellow-600">
                {filteredData.filter(item => item.utilization >= 80 && item.utilization < 100).length}
              </div>
              <div className="text-gray-600">Warning</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-red-600">
                {overBudgetCount}
              </div>
              <div className="text-gray-600">Over Budget</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};