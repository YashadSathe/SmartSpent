import React from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { getPieChartConfig } from '../../utils/chartConfig';
import type { CategorySpending } from '../../types';

// Register Chart.js components we need for pie chart
ChartJS.register(ArcElement, Tooltip, Legend);

// Props for spending chart component
interface SpendingChartProps {
  data: CategorySpending[];
  className?: string;
}

export const SpendingChart: React.FC<SpendingChartProps> = ({ 
  data, 
  className = '' 
}) => {
  // Filter out categories with zero spending for cleaner chart
  const filteredData = data.filter(item => item.spent > 0);
  
  // Get chart configuration based on data
  const chartConfig = getPieChartConfig(filteredData);

  // Calculate total spent for summary
  const totalSpent = filteredData.reduce((sum, item) => sum + item.spent, 0);

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
      {/* Chart header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Spending by Category
          </h3>
          <p className="text-sm text-gray-500">
            Total: ₹{totalSpent.toLocaleString()}
          </p>
        </div>
      </div>

      {/* Chart container */}
      <div className="h-80">
        {filteredData.length > 0 ? (
          // Render pie chart if we have data
          <Pie data={chartConfig.data} options={chartConfig.options} />
        ) : (
          // Show empty state if no data
          <div className="h-full flex items-center justify-center text-gray-500">
            <div className="text-center">
              <div className="text-4xl mb-2">📊</div>
              <p>No spending data available</p>
              <p className="text-sm">Add some expenses to see charts</p>
            </div>
          </div>
        )}
      </div>

      {/* Additional summary information */}
      {filteredData.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Top Category:</span>
              <span className="font-medium ml-2">
                {filteredData[0]?.category || 'N/A'}
              </span>
            </div>
            <div>
              <span className="text-gray-600">Categories:</span>
              <span className="font-medium ml-2">{filteredData.length}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};