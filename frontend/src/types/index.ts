// Expense related types
export interface Expense {
  id: number;
  expense_name: string;
  amount: number;
  category: string;
  predicted_category?: string;
  confidence?: number;
  user_corrected: boolean;
  created_at: string;
}

export interface ExpenseCreate {
  expense_name: string;
  amount: number;
  category?: string;
}

export interface ExpenseUpdate {
  expense_name?: string;
  amount?: number;
  category?: string;
}

// Budget related types
export interface Budget {
  monthly_budget: number;
  monthly_income: number;
}

export interface CategoryBudget {
  id: number;
  category: string;
  monthly_budget: number;
  created_at: string;
}

// Classification types
export interface Classification {
  category: string;
  confidence: number;
  suggested_categories: string[];
}

// Dashboard types
export interface DashboardSummary {
  total_spent: number;
  total_budget: number;
  budget_utilization: number;
  savings: number;
  savings_rate: number;
  total_income: number;
}

export interface CategorySpending {
  category: string;
  spent: number;
  budget: number;
  remaining: number;
  utilization: number;
}