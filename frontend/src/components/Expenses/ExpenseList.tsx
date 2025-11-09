import React, { useState } from 'react';
import { Edit2, Trash2, Calendar, IndianRupee } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { ConfidenceBadge } from '../Common/ConfidenceBadge';
import { CategoryIcon } from '../Common/CategoryIcon';
import { LoadingSpinner } from '../Common/LoadingSpinner';
import type { Expense } from '../../types';

// Props for expense list component
interface ExpenseListProps {
  expenses: Expense[];
  showCurrentMonthOnly?: boolean;
}

export const ExpenseList: React.FC<ExpenseListProps> = ({ 
  expenses, 
  showCurrentMonthOnly = false 
}) => {
  // Access global app state and functions
  const { updateExpense, deleteExpense, loading } = useApp();
  
  // Local state for editing
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<Partial<Expense>>({});

  // Handle starting edit mode
  const startEdit = (expense: Expense) => {
    setEditingId(expense.id);
    setEditForm({
      expense_name: expense.expense_name,
      amount: expense.amount,
      category: expense.category
    });
  };

  // Handle canceling edit
  const cancelEdit = () => {
    setEditingId(null);
    setEditForm({});
  };

  // Handle saving edits
  const saveEdit = async (id: number) => {
    try {
      await updateExpense(id, editForm);
      setEditingId(null);
      setEditForm({});
    } catch (error) {
      console.error('Failed to update expense:', error);
    }
  };

  // Handle deleting expense
  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this expense?')) {
      try {
        await deleteExpense(id);
      } catch (error) {
        console.error('Failed to delete expense:', error);
      }
    }
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Show loading spinner if data is being fetched
  if (loading && expenses.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <div className="flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
        <p className="text-center text-gray-500 mt-4">Loading expenses...</p>
      </div>
    );
  }

  // Show empty state if no expenses
  if (expenses.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
        <div className="text-6xl mb-4">💸</div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          No expenses yet
        </h3>
        <p className="text-gray-500">
          {showCurrentMonthOnly 
            ? "You haven't added any expenses this month."
            : "Get started by adding your first expense!"
          }
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      {/* List header */}
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">
          {showCurrentMonthOnly ? 'This Month\'s Expenses' : 'All Expenses'}
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          {expenses.length} expense{expenses.length !== 1 ? 's' : ''} total
        </p>
      </div>

      {/* Expenses list */}
      <div className="divide-y divide-gray-200">
        {expenses.map((expense) => (
          <div key={expense.id} className="p-6 hover:bg-gray-50 transition-colors">
            {editingId === expense.id ? (
              // Edit mode
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <input
                      type="text"
                      value={editForm.expense_name || ''}
                      onChange={(e) => setEditForm(prev => ({ 
                        ...prev, 
                        expense_name: e.target.value 
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Amount (₹)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={editForm.amount || ''}
                      onChange={(e) => setEditForm(prev => ({ 
                        ...prev, 
                        amount: parseFloat(e.target.value) 
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={() => saveEdit(expense.id)}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    Save
                  </button>
                  <button
                    onClick={cancelEdit}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              // Display mode
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 flex-1">
                  {/* Category Icon */}
                  <CategoryIcon 
                    category={expense.category} 
                    className="text-gray-600"
                  />
                  
                  {/* Expense Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-medium text-gray-900 truncate">
                        {expense.expense_name}
                      </h4>
                      
                      {/* AI Confidence Badge if available */}
                      {expense.confidence && expense.predicted_category && (
                        <ConfidenceBadge 
                          confidence={expense.confidence} 
                          size="sm" 
                          showLabel={false}
                        />
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      {/* Category */}
                      <span className="flex items-center space-x-1">
                        <span>📁</span>
                        <span>{expense.category}</span>
                        {expense.user_corrected && (
                          <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">
                            Corrected
                          </span>
                        )}
                      </span>
                      
                      {/* Date */}
                      <span className="flex items-center space-x-1">
                        <Calendar className="w-3 h-3" />
                        <span>{formatDate(expense.created_at)}</span>
                      </span>
                    </div>
                  </div>
                </div>
                
                {/* Amount and Actions */}
                <div className="flex items-center space-x-4">
                  {/* Amount */}
                  <div className="text-right">
                    <div className="font-semibold text-gray-900 flex items-center space-x-1">
                      <IndianRupee className="w-4 h-4" />
                      <span>{expense.amount.toLocaleString()}</span>
                    </div>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => startEdit(expense)}
                      className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                      title="Edit expense"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(expense.id)}
                      className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Delete expense"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};