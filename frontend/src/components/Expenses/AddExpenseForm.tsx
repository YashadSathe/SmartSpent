import React, { useState, useEffect } from 'react';
import { Plus, Loader, Check, X } from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { classificationApi } from '../../services/api';
import { ConfidenceBadge } from '../Common/ConfidenceBadge';
import { CategoryIcon } from '../Common/CategoryIcon';
import { LoadingSpinner } from '../Common/LoadingSpinner';
import type { Classification } from '../../types';

// Props for add expense form component
interface AddExpenseFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const AddExpenseForm: React.FC<AddExpenseFormProps> = ({
  isOpen,
  onClose,
  onSuccess
}) => {
  // Access global app state and functions
  const { addExpense, loading } = useApp();
  
  // Form state
  const [formData, setFormData] = useState({
    expense_name: '',
    amount: '',
    category: ''
  });
  
  // AI classification state
  const [classification, setClassification] = useState<Classification | null>(null);
  const [isClassifying, setIsClassifying] = useState(false);
  const [showCategorySuggestions, setShowCategorySuggestions] = useState(false);

  // Reset form when opened/closed
  useEffect(() => {
    if (isOpen) {
      setFormData({ expense_name: '', amount: '', category: '' });
      setClassification(null);
      setShowCategorySuggestions(false);
    }
  }, [isOpen]);

  // Auto-classify when expense name changes (with debounce)
  useEffect(() => {
    if (!formData.expense_name.trim() || formData.category) return;

    const timer = setTimeout(async () => {
      setIsClassifying(true);
      try {
        const result = await classificationApi.predict(formData.expense_name);
        setClassification(result);
        
        // Auto-select category if confidence is high
        if (result.confidence >= 0.8) {
          setFormData(prev => ({ ...prev, category: result.category }));
        }
      } catch (error) {
        console.error('Classification failed:', error);
      } finally {
        setIsClassifying(false);
      }
    }, 500); // Wait 500ms after user stops typing

    return () => clearTimeout(timer);
  }, [formData.expense_name, formData.category]);

  // Handle form input changes
  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Reset classification if user manually selects category
    if (field === 'category' && value) {
      setClassification(null);
    }
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.expense_name.trim() || !formData.amount || !formData.category) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      await addExpense({
        expense_name: formData.expense_name.trim(),
        amount: parseFloat(formData.amount),
        category: formData.category
      });
      
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Failed to add expense:', error);
    }
  };

  // If form is not open, don't render anything
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Form header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            Add New Expense
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Expense Name Field */}
          <div>
            <label htmlFor="expense_name" className="block text-sm font-medium text-gray-700 mb-2">
              What did you spend on? *
            </label>
            <div className="relative">
              <input
                type="text"
                id="expense_name"
                value={formData.expense_name}
                onChange={(e) => handleInputChange('expense_name', e.target.value)}
                placeholder="e.g., Starbucks coffee, Uber ride, Netflix subscription"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                required
              />
              
              {/* AI Classification Indicator */}
              {isClassifying && (
                <div className="absolute right-3 top-3">
                  <LoadingSpinner size="sm" />
                </div>
              )}
            </div>
            
            {/* AI Classification Result */}
            {classification && !formData.category && (
              <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <CategoryIcon category={classification.category} size={16} />
                    <span className="font-medium">{classification.category}</span>
                    <ConfidenceBadge confidence={classification.confidence} size="sm" />
                  </div>
                  <button
                    type="button"
                    onClick={() => handleInputChange('category', classification.category)}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    Use This
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Amount Field */}
          <div>
            <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
              Amount (₹) *
            </label>
            <input
              type="number"
              id="amount"
              step="0.01"
              min="0"
              value={formData.amount}
              onChange={(e) => handleInputChange('amount', e.target.value)}
              placeholder="0.00"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            />
          </div>

          {/* Category Field */}
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
              Category *
            </label>
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowCategorySuggestions(!showCategorySuggestions)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg text-left focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white"
              >
                {formData.category ? (
                  <div className="flex items-center space-x-2">
                    <CategoryIcon category={formData.category} size={20} />
                    <span>{formData.category}</span>
                  </div>
                ) : (
                  <span className="text-gray-500">Select a category...</span>
                )}
              </button>

              {/* Category Dropdown */}
              {showCategorySuggestions && classification && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {classification.suggested_categories.map((category) => (
                    <button
                      key={category}
                      type="button"
                      onClick={() => {
                        handleInputChange('category', category);
                        setShowCategorySuggestions(false);
                      }}
                      className={`w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center space-x-3 ${
                        category === formData.category ? 'bg-primary-50 text-primary-700' : ''
                      }`}
                    >
                      <CategoryIcon category={category} size={20} />
                      <span>{category}</span>
                      {category === classification.category && (
                        <ConfidenceBadge confidence={classification.confidence} size="sm" showLabel={false} />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  <span>Adding...</span>
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  <span>Add Expense</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};