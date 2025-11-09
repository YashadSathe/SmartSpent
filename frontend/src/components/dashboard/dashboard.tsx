import React from 'react';
import { SummaryCards } from './SummaryCards';
import { SpendingChart } from './SpendingChart';
import { BudgetProgress } from './BudgetProgress';
import { ExpenseList } from '../Expenses/ExpenseList';
import type { DashboardSummary, CategorySpending, Expense } from '../../types';

// Props for main dashboard component
interface DashboardProps {
  summary: DashboardSummary;
  categorySpending: CategorySpending[];
  recentExpenses: Expense[];
}

export const Dashboard: React.FC<DashboardProps> = ({
  summary,
  categorySpending,
  recentExpenses
}) => {
  return (
    <div className="space-y-8">
      {/* Summary Cards - Top Metrics */}
      <SummaryCards data={summary} />

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Spending by Category Pie Chart */}
        <SpendingChart data={categorySpending} />
        
        {/* Budget Utilization Bar Chart */}
        <BudgetProgress data={categorySpending} />
      </div>

      {/* Recent Expenses Section */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Recent Expenses List */}
        <div className="xl:col-span-2">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                Recent Expenses
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                Your latest transactions this month
              </p>
            </div>
            <div className="p-1">
              {recentExpenses.length > 0 ? (
                <div className="space-y-1">
                  {recentExpenses.map((expense) => (
                    <div
                      key={expense.id}
                      className="flex items-center justify-between p-4 hover:bg-gray-50 rounded-lg transition-colors"
                    >
                      <div className="flex items-center space-x-3 flex-1 min-w-0">
                        <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                          <span className="text-lg">
                            {expense.category === 'Food' && '🍕'}
                            {expense.category === 'Drinks' && '☕'}
                            {expense.category === 'Transport' && '🚗'}
                            {expense.category === 'Shopping' && '🛍️'}
                            {expense.category === 'Entertainment' && '🎬'}
                            {expense.category === 'Bills' && '🧾'}
                            {expense.category === 'Healthcare' && '🏥'}
                            {expense.category === 'Education' && '📚'}
                            {expense.category === 'Travel' && '✈️'}
                            {expense.category === 'Groceries' && '🛒'}
                            {expense.category === 'Personal Care' && '💇'}
                            {expense.category === 'Other' && '📦'}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-gray-900 truncate">
                            {expense.expense_name}
                          </h4>
                          <p className="text-sm text-gray-500">
                            {expense.category} • {new Date(expense.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-gray-900">
                          ₹{expense.amount.toLocaleString()}
                        </div>
                        {expense.confidence && (
                          <div className="text-xs text-gray-500 mt-1">
                            {Math.round(expense.confidence * 100)}% confident
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-gray-500">
                  <div className="text-4xl mb-2">💸</div>
                  <p>No expenses yet this month</p>
                  <p className="text-sm">Add your first expense to see it here</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Stats Sidebar */}
        <div className="space-y-6">
          {/* Monthly Summary */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h4 className="font-semibold text-gray-900 mb-4">Monthly Summary</h4>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Income:</span>
                <span className="font-medium text-green-600">
                  ₹{summary.total_income.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Spent:</span>
                <span className="font-medium text-gray-900">
                  ₹{summary.total_spent.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Savings:</span>
                <span className={`font-medium ${
                  summary.savings >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  ₹{Math.abs(summary.savings).toLocaleString()}
                </span>
              </div>
              <div className="pt-3 border-t border-gray-200">
                <div className="flex justify-between">
                  <span className="text-gray-600">Savings Rate:</span>
                  <span className={`font-medium ${
                    summary.savings_rate >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {Math.abs(summary.savings_rate).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Budget Status */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h4 className="font-semibold text-gray-900 mb-4">Budget Status</h4>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Budget Used</span>
                  <span className="font-medium">{summary.budget_utilization.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      summary.budget_utilization >= 100 ? 'bg-red-500' :
                      summary.budget_utilization >= 80 ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(summary.budget_utilization, 100)}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {categorySpending.filter(cat => cat.utilization < 80).length}
                  </div>
                  <div className="text-gray-600">On Track</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {categorySpending.filter(cat => cat.utilization >= 100).length}
                  </div>
                  <div className="text-gray-600">Over Budget</div>
                </div>
              </div>
            </div>
          </div>

          {/* AI Insights */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
            <h4 className="font-semibold text-blue-900 mb-2">AI Insights</h4>
            <p className="text-blue-800 text-sm">
              Your expenses are automatically categorized with {''}
              <span className="font-medium">90%+ accuracy</span> using our AI system.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};