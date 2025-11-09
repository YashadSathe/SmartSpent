import React, { createContext, useContext, useReducer, useEffect } from 'react';
import type { Expense, Budget, CategoryBudget, DashboardSummary, CategorySpending } from '../types';
import { expenseApi, budgetApi, dashboardApi } from '../services/api';

interface AppState {
  expenses: Expense[];
  currentMonthExpenses: Expense[];
  overallBudget: Budget;
  categoryBudgets: CategoryBudget[];
  dashboardSummary: DashboardSummary | null;
  categorySpending: CategorySpending[];
  loading: boolean;
  error: string | null;
}

type AppAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_EXPENSES'; payload: Expense[] }
  | { type: 'SET_CURRENT_MONTH_EXPENSES'; payload: Expense[] }
  | { type: 'SET_OVERALL_BUDGET'; payload: Budget }
  | { type: 'SET_CATEGORY_BUDGETS'; payload: CategoryBudget[] }
  | { type: 'SET_DASHBOARD_SUMMARY'; payload: DashboardSummary }
  | { type: 'SET_CATEGORY_SPENDING'; payload: CategorySpending[] }
  | { type: 'ADD_EXPENSE'; payload: Expense }
  | { type: 'UPDATE_EXPENSE'; payload: Expense }
  | { type: 'DELETE_EXPENSE'; payload: number };

const initialState: AppState = {
  expenses: [],
  currentMonthExpenses: [],
  overallBudget: { monthly_budget: 0, monthly_income: 0 },
  categoryBudgets: [],
  dashboardSummary: null,
  categorySpending: [],
  loading: false,
  error: null,
};

const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_EXPENSES':
      return { ...state, expenses: action.payload };
    case 'SET_CURRENT_MONTH_EXPENSES':
      return { ...state, currentMonthExpenses: action.payload };
    case 'SET_OVERALL_BUDGET':
      return { ...state, overallBudget: action.payload };
    case 'SET_CATEGORY_BUDGETS':
      return { ...state, categoryBudgets: action.payload };
    case 'SET_DASHBOARD_SUMMARY':
      return { ...state, dashboardSummary: action.payload };
    case 'SET_CATEGORY_SPENDING':
      return { ...state, categorySpending: action.payload };
    case 'ADD_EXPENSE':
      return { 
        ...state, 
        expenses: [action.payload, ...state.expenses],
        currentMonthExpenses: [action.payload, ...state.currentMonthExpenses],
      };
    case 'UPDATE_EXPENSE':
      return {
        ...state,
        expenses: state.expenses.map(exp => 
          exp.id === action.payload.id ? action.payload : exp
        ),
        currentMonthExpenses: state.currentMonthExpenses.map(exp =>
          exp.id === action.payload.id ? action.payload : exp
        ),
      };
    case 'DELETE_EXPENSE':
      return {
        ...state,
        expenses: state.expenses.filter(exp => exp.id !== action.payload),
        currentMonthExpenses: state.currentMonthExpenses.filter(exp => exp.id !== action.payload),
      };
    default:
      return state;
  }
};

interface AppContextType extends AppState {
  refreshData: () => Promise<void>;
  addExpense: (expense: Omit<Expense, 'id' | 'created_at'>) => Promise<void>;
  updateExpense: (id: number, expense: Partial<Expense>) => Promise<void>;
  deleteExpense: (id: number) => Promise<void>;
  setOverallBudget: (budget: Budget) => Promise<void>;
  setCategoryBudget: (category: string, budget: number) => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const setLoading = (loading: boolean) => dispatch({ type: 'SET_LOADING', payload: loading });
  const setError = (error: string | null) => dispatch({ type: 'SET_ERROR', payload: error });

  const refreshData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [
        expenses,
        currentMonthExpenses,
        overallBudget,
        categoryBudgets,
        dashboardSummary,
        categorySpending,
      ] = await Promise.all([
        expenseApi.getAll(),
        expenseApi.getCurrentMonth(),
        budgetApi.getOverall(),
        budgetApi.getCategoryBudgets(),
        dashboardApi.getSummary(),
        dashboardApi.getCategorySpending(),
      ]);

      dispatch({ type: 'SET_EXPENSES', payload: expenses });
      dispatch({ type: 'SET_CURRENT_MONTH_EXPENSES', payload: currentMonthExpenses });
      dispatch({ type: 'SET_OVERALL_BUDGET', payload: overallBudget });
      dispatch({ type: 'SET_CATEGORY_BUDGETS', payload: categoryBudgets });
      dispatch({ type: 'SET_DASHBOARD_SUMMARY', payload: dashboardSummary });
      dispatch({ type: 'SET_CATEGORY_SPENDING', payload: categorySpending });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const addExpense = async (expenseData: Omit<Expense, 'id' | 'created_at'>) => {
    try {
      const newExpense = await expenseApi.create(expenseData);
      dispatch({ type: 'ADD_EXPENSE', payload: newExpense });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add expense');
      throw err;
    }
  };

  const updateExpense = async (id: number, expenseData: Partial<Expense>) => {
    try {
      const updatedExpense = await expenseApi.update(id, expenseData);
      dispatch({ type: 'UPDATE_EXPENSE', payload: updatedExpense });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update expense');
      throw err;
    }
  };

  const deleteExpense = async (id: number) => {
    try {
      await expenseApi.delete(id);
      dispatch({ type: 'DELETE_EXPENSE', payload: id });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete expense');
      throw err;
    }
  };

  const setOverallBudget = async (budget: Budget) => {
    try {
      await budgetApi.setOverall(budget);
      dispatch({ type: 'SET_OVERALL_BUDGET', payload: budget });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to set budget');
      throw err;
    }
  };

  const setCategoryBudget = async (category: string, budget: number) => {
    try {
      const updatedBudget = await budgetApi.setCategoryBudget({ category, monthly_budget: budget });
      dispatch({ type: 'SET_CATEGORY_BUDGETS', payload: 
        state.categoryBudgets.map(cb => 
          cb.category === category ? updatedBudget : cb
        )
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to set category budget');
      throw err;
    }
  };

  useEffect(() => {
    refreshData();
  }, []);

  const contextValue: AppContextType = {
    ...state,
    refreshData,
    addExpense,
    updateExpense,
    deleteExpense,
    setOverallBudget,
    setCategoryBudget,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};