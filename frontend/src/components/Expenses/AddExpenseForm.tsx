import React, { useState, useEffect, useRef } from 'react';
import { Plus, Loader, X, Upload, Camera } from 'lucide-react'; // Added icons
import { useApp } from '../../contexts/AppContext';
import { classificationApi, expenseApi } from '../../services/api'; // Import expenseApi
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

export const AddExpenseForm: React.FC<AddExpenseFormProps> = ({ isOpen, onClose, onSuccess }) => {
  // Access global app state and functions
  // Added refreshData to update dashboard after scan
  const { addExpense, refreshData, loading } = useApp();
  
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

  // --- NEW: Scanning State ---
  const [isScanning, setIsScanning] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Reset form when opened/closed
  useEffect(() => {
    if (isOpen) {
      setFormData({ expense_name: '', amount: '', category: '' });
      setClassification(null);
      setShowCategorySuggestions(false);
      setIsScanning(false);
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
    }, 500); 

    return () => clearTimeout(timer);
  }, [formData.expense_name, formData.category]);

  // --- NEW: Handle File Upload for Scanning ---
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsScanning(true);
    try {
      // Call the API to upload and process the receipt
      const result = await expenseApi.uploadReceipt(file);
      
      alert(`Success! Added ${result.items_count} items from ${result.extracted_data?.merchant_name || 'receipt'}.`);
      
      await refreshData(); // Refresh the dashboard to show new expenses
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Receipt scan failed:', error);
      alert('Failed to scan receipt. Please try again or enter manually.');
    } finally {
      setIsScanning(false);
      // Reset file input so same file can be selected again if needed
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  // Handle form input changes
  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Form header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            Add New Expense
          </h2>
          <button
            onClick={onClose}
            className="p-2 transition-colors rounded-lg hover:bg-gray-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          
          {/* --- NEW: Scan Receipt Section --- */}
          <div className="p-4 border border-blue-100 rounded-lg bg-blue-50">
            <div className="flex items-center justify-between mb-3">
              <div className="text-sm font-medium text-blue-800">Have a receipt?</div>
              <span className="text-xs bg-blue-200 text-blue-800 px-2 py-0.5 rounded-full">AI Powered</span>
            </div>
            
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileUpload} 
              accept="image/*,application/pdf" 
              className="hidden" 
            />
            
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isScanning}
              className="w-full py-2.5 bg-white border border-blue-300 text-blue-700 rounded-lg hover:bg-blue-50 flex items-center justify-center gap-2 font-medium transition-colors shadow-sm"
            >
              {isScanning ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  <span>Scanning & Categorizing...</span>
                </>
              ) : (
                <>
                  <Camera className="w-4 h-4" />
                  <span>Scan Receipt / Invoice</span>
                </>
              )}
            </button>
          </div>
          
          <div className="relative flex items-center py-2">
            <div className="flex-grow border-t border-gray-300"></div>
            <span className="flex-shrink-0 mx-4 text-xs font-medium tracking-wider text-gray-400 uppercase">Or enter manually</span>
            <div className="flex-grow border-t border-gray-300"></div>
          </div>

          {/* Manual Entry Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Expense Name Field */}
            <div>
              <label htmlFor="expense_name" className="block mb-2 text-sm font-medium text-gray-700">
                What did you spend on? *
              </label>
              <div className="relative">
                <input
                  type="text"
                  id="expense_name"
                  value={formData.expense_name}
                  onChange={(e) => handleInputChange('expense_name', e.target.value)}
                  placeholder="e.g., Starbucks coffee, Uber ride"
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
                <div className="p-3 mt-2 border border-blue-200 rounded-lg bg-blue-50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <CategoryIcon category={classification.category} size={16} />
                      <span className="font-medium">{classification.category}</span>
                      <ConfidenceBadge confidence={classification.confidence} size="sm" />
                    </div>
                    <button
                      type="button"
                      onClick={() => handleInputChange('category', classification.category)}
                      className="text-sm font-medium text-blue-600 hover:text-blue-800"
                    >
                      Use This
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Amount Field */}
            <div>
              <label htmlFor="amount" className="block mb-2 text-sm font-medium text-gray-700">
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
              <label htmlFor="category" className="block mb-2 text-sm font-medium text-gray-700">
                Category *
              </label>
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowCategorySuggestions(!showCategorySuggestions)}
                  className="w-full px-4 py-3 text-left bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
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
                  <div className="absolute z-10 w-full mt-1 overflow-y-auto bg-white border border-gray-300 rounded-lg shadow-lg max-h-60">
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
            <div className="flex pt-4 space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-3 text-gray-700 transition-colors border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex items-center justify-center flex-1 px-4 py-3 space-x-2 text-white transition-colors rounded-lg bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
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
    </div>
  );
};