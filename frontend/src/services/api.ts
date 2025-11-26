import axios from 'axios';
import type { 
  Expense, ExpenseCreate, ExpenseUpdate, 
  Budget, CategoryBudget, Classification,
  DashboardSummary, CategorySpending 
} from '../types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Expense API
export const expenseApi = {
  // Get all expenses
  getAll: (): Promise<Expense[]> => 
    api.get('/expenses/').then(res => res.data),
  
  // Get current month expenses
  getCurrentMonth: (): Promise<Expense[]> => 
    api.get('/expenses/current-month').then(res => res.data),
  
  // Create new expense
  create: (expense: ExpenseCreate): Promise<Expense> => 
    api.post('/expenses/', expense).then(res => res.data),
  
  // Update expense
  update: (id: number, expense: ExpenseUpdate): Promise<Expense> => 
    api.put(`/expenses/${id}`, expense).then(res => res.data),
  
  // Delete expense
  delete: (id: number): Promise<void> => 
    api.delete(`/expenses/${id}`).then(res => res.data),

  // Upload receipt/invoice
  uploadReceipt: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/expenses/upload-receipt', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Classification API
export const classificationApi = {
  // Classify expense text
  predict: (expenseName: string): Promise<Classification> => 
    api.post('/classification/predict', { expense_name: expenseName }).then(res => res.data),
  
  // Get all categories
  getCategories: (): Promise<{ categories: string[] }> => 
    api.get('/classification/categories').then(res => res.data),
};

// Budget API
export const budgetApi = {
  // Get overall budget
  getOverall: (): Promise<Budget> => 
    api.get('/budget/overall').then(res => res.data),
  
  // Set overall budget
  setOverall: (budget: Budget): Promise<{ message: string }> => 
    api.post('/budget/overall', budget).then(res => res.data),
  
  // Get all category budgets
  getCategoryBudgets: (): Promise<CategoryBudget[]> => 
    api.get('/budget/categories').then(res => res.data),
  
  // Set category budget
  setCategoryBudget: (budget: Omit<CategoryBudget, 'id' | 'created_at'>): Promise<CategoryBudget> => 
    api.post('/budget/category', budget).then(res => res.data),
};

// Dashboard API
export const dashboardApi = {
  // Get dashboard summary
  getSummary: (): Promise<DashboardSummary> => 
    api.get('/dashboard/summary').then(res => res.data),
  
  // Get category spending breakdown
  getCategorySpending: (): Promise<CategorySpending[]> => 
    api.get('/dashboard/category-spending').then(res => res.data),
  
  // Get recent expenses
  getRecentExpenses: (): Promise<Expense[]> => 
    api.get('/dashboard/recent-expenses').then(res => res.data),
};

export default api;