import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider, useApp } from './contexts/AppContext';
import { Dashboard } from './components/Dashboard/Dashboard';
import { ExpenseList } from './components/Expenses/ExpenseList';
import { BudgetConfig } from './components/Budget/BudgetConfig';
import { AddExpenseForm } from './components/Expenses/AddExpenseForm';
import { LoadingSpinner } from './components/Common/LoadingSpinner';
import { Navigation } from './components/Common/Navigation';
import './styles/globals.css';

// Main layout component that wraps all pages
const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { loading, error } = useApp();
  const [isAddExpenseOpen, setIsAddExpenseOpen] = useState(false);

  // Handle successful expense addition
  const handleExpenseAdded = () => {
    // The context will automatically refresh data
    console.log('Expense added successfully!');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <Navigation onAddExpense={() => setIsAddExpenseOpen(true)} />
      
      {/* Main Content Area */}
      <main className="container mx-auto px-4 py-8">
        {/* Global Loading Overlay */}
        {loading && (
          <div className="fixed inset-0 bg-white bg-opacity-80 flex items-center justify-center z-50">
            <div className="text-center">
              <LoadingSpinner size="lg" />
              <p className="mt-4 text-gray-600">Loading your financial data...</p>
            </div>
          </div>
        )}

        {/* Global Error Banner */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-red-600">⚠️</span>
                <span className="text-red-800 font-medium">Error:</span>
                <span className="text-red-700">{error}</span>
              </div>
              <button
                onClick={() => window.location.reload()}
                className="text-red-600 hover:text-red-800 text-sm font-medium"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Page Content */}
        {children}
      </main>

      {/* Add Expense Modal */}
      <AddExpenseForm
        isOpen={isAddExpenseOpen}
        onClose={() => setIsAddExpenseOpen(false)}
        onSuccess={handleExpenseAdded}
      />
    </div>
  );
};

// Dashboard Page Component
const DashboardPage: React.FC = () => {
  const { dashboardSummary, categorySpending, currentMonthExpenses } = useApp();

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Welcome to SmartSpent
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Your AI-powered expense tracker that automatically categorizes spending 
          and helps you stay on budget.
        </p>
      </div>

      {/* Dashboard Components */}
      {dashboardSummary && (
        <Dashboard 
          summary={dashboardSummary}
          categorySpending={categorySpending}
          recentExpenses={currentMonthExpenses.slice(0, 5)}
        />
      )}
    </div>
  );
};

// Expenses Page Component
const ExpensesPage: React.FC = () => {
  const { currentMonthExpenses } = useApp();

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Expenses</h1>
          <p className="text-gray-600 mt-1">
            Manage and review your spending history
          </p>
        </div>
      </div>

      {/* Expenses List */}
      <ExpenseList 
        expenses={currentMonthExpenses}
        showCurrentMonthOnly={true}
      />
    </div>
  );
};

// All Expenses Page Component
const AllExpensesPage: React.FC = () => {
  const { expenses } = useApp();

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">All Expenses</h1>
          <p className="text-gray-600 mt-1">
            Complete history of all your expenses
          </p>
        </div>
      </div>

      {/* All Expenses List */}
      <ExpenseList expenses={expenses} />
    </div>
  );
};

// Budget Page Component
const BudgetPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Budget Settings</h1>
        <p className="text-gray-600 mt-1">
          Configure your monthly budgets and spending limits
        </p>
      </div>

      {/* Budget Configuration */}
      <BudgetConfig />
    </div>
  );
};

// Main App Component with Routing
const AppContent: React.FC = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          {/* Dashboard - Default Route */}
          <Route path="/" element={<DashboardPage />} />
          
          {/* Current Month Expenses */}
          <Route path="/expenses" element={<ExpensesPage />} />
          
          {/* All Expenses History */}
          <Route path="/expenses/all" element={<AllExpensesPage />} />
          
          {/* Budget Configuration */}
          <Route path="/budget" element={<BudgetPage />} />
          
          {/* Catch-all route - redirect to dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
};

// Root App Component with Provider
const App: React.FC = () => {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
};

export default App;