import React, { useState } from 'react';
import { Save, Target, Wallet } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { LoadingSpinner } from '../Common/LoadingSpinner';
import type { Budget, CategoryBudget } from '../../types';

// Props for budget configuration component
interface BudgetConfigProps {
  className?: string;
}

export const BudgetConfig: React.FC<BudgetConfigProps> = ({ className = '' }) => {
  // Access global app state and functions
  const { 
    overallBudget, 
    categoryBudgets, 
    setOverallBudget, 
    setCategoryBudget, 
    loading 
  } = useApp();
  
  // Local state for form inputs
  const [overallForm, setOverallForm] = useState<Budget>(overallBudget);
  const [categoryForms, setCategoryForms] = useState<{ [key: string]: number }>({});
  const [isSaving, setIsSaving] = useState(false);

  // Initialize forms when data loads
  React.useEffect(() => {
    setOverallForm(overallBudget);
    
    const initialCategoryForms: { [key: string]: number } = {};
    categoryBudgets.forEach(budget => {
      initialCategoryForms[budget.category] = budget.monthly_budget;
    });
    setCategoryForms(initialCategoryForms);
  }, [overallBudget, categoryBudgets]);

  // Handle overall budget form submission
  const handleOverallBudgetSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await setOverallBudget(overallForm);
    } catch (error) {
      console.error('Failed to save overall budget:', error);
    } finally {
      setIsSaving(false);
    }
  };

  // Handle category budget changes
  const handleCategoryBudgetChange = (category: string, value: number) => {
    setCategoryForms(prev => ({
      ...prev,
      [category]: value
    }));
  };

  // Handle category budget save
  const handleCategoryBudgetSave = async (category: string, budget: number) => {
    try {
      await setCategoryBudget(category, budget);
    } catch (error) {
      console.error(`Failed to save ${category} budget:`, error);
    }
  };

  // Calculate total category budgets
  const totalCategoryBudgets = Object.values(categoryForms).reduce((sum, budget) => sum + budget, 0);
  
  // Check if category budgets exceed overall budget
  const isOverBudget = totalCategoryBudgets > overallForm.monthly_budget;

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Overall Budget Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Target className="w-6 h-6 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            Overall Monthly Budget
          </h3>
        </div>

        <form onSubmit={handleOverallBudgetSave} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Monthly Income */}
            <div>
              <label htmlFor="monthly_income" className="block text-sm font-medium text-gray-700 mb-2">
                Monthly Income (₹)
              </label>
              <input
                type="number"
                id="monthly_income"
                step="100"
                min="0"
                value={overallForm.monthly_income || ''}
                onChange={(e) => setOverallForm(prev => ({ 
                  ...prev, 
                  monthly_income: parseFloat(e.target.value) || 0 
                }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Enter your monthly income"
              />
            </div>

            {/* Monthly Budget */}
            <div>
              <label htmlFor="monthly_budget" className="block text-sm font-medium text-gray-700 mb-2">
                Monthly Spending Budget (₹)
              </label>
              <input
                type="number"
                id="monthly_budget"
                step="100"
                min="0"
                value={overallForm.monthly_budget || ''}
                onChange={(e) => setOverallForm(prev => ({ 
                  ...prev, 
                  monthly_budget: parseFloat(e.target.value) || 0 
                }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Enter your spending limit"
              />
            </div>
          </div>

          {/* Budget Summary */}
          {overallForm.monthly_income > 0 && overallForm.monthly_budget > 0 && (
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Expected Savings:</span>
                  <div className="font-semibold text-green-600">
                    ₹{(overallForm.monthly_income - overallForm.monthly_budget).toLocaleString()}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600">Savings Rate:</span>
                  <div className="font-semibold text-green-600">
                    {((1 - overallForm.monthly_budget / overallForm.monthly_income) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Save Button */}
          <button
            type="submit"
            disabled={isSaving}
            className="w-full md:w-auto px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
          >
            {isSaving ? (
              <>
                <LoadingSpinner size="sm" />
                <span>Saving...</span>
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>Save Overall Budget</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Category Budgets Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Wallet className="w-6 h-6 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            Category Budgets
          </h3>
        </div>

        {/* Budget Warning */}
        {isOverBudget && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center space-x-2 text-red-800">
              <span>⚠️</span>
              <span className="font-medium">Warning:</span>
              <span>
                Category budgets (₹{totalCategoryBudgets.toLocaleString()}) exceed 
                overall budget (₹{overallForm.monthly_budget.toLocaleString()})
              </span>
            </div>
          </div>
        )}

        {/* Category Budgets Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {categoryBudgets.map((categoryBudget) => (
            <div
              key={categoryBudget.category}
              className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900">
                  {categoryBudget.category}
                </h4>
                <span className="text-sm text-gray-500">
                  {((categoryForms[categoryBudget.category] || 0) / overallForm.monthly_budget * 100).toFixed(1)}%
                </span>
              </div>

              <div className="space-y-2">
                <input
                  type="number"
                  step="100"
                  min="0"
                  value={categoryForms[categoryBudget.category] || ''}
                  onChange={(e) => handleCategoryBudgetChange(
                    categoryBudget.category, 
                    parseFloat(e.target.value) || 0
                  )}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="0"
                />
                
                <button
                  onClick={() => handleCategoryBudgetSave(
                    categoryBudget.category, 
                    categoryForms[categoryBudget.category] || 0
                  )}
                  disabled={loading}
                  className="w-full px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors flex items-center justify-center space-x-1"
                >
                  <Save className="w-3 h-3" />
                  <span>Save</span>
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Category Budgets Summary */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Total Category Budgets:</span>
              <div className={`font-semibold ${isOverBudget ? 'text-red-600' : 'text-gray-900'}`}>
                ₹{totalCategoryBudgets.toLocaleString()}
              </div>
            </div>
            <div>
              <span className="text-gray-600">Remaining:</span>
              <div className={`font-semibold ${
                overallForm.monthly_budget - totalCategoryBudgets < 0 
                  ? 'text-red-600' 
                  : 'text-green-600'
              }`}>
                ₹{(overallForm.monthly_budget - totalCategoryBudgets).toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};