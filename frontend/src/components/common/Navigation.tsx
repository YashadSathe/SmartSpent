import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Receipt, 
  Wallet, 
  BarChart3, 
  Plus,
  Menu,
  X 
} from 'lucide-react';

// Props for navigation component
interface NavigationProps {
  onAddExpense: () => void;
}

export const Navigation: React.FC<NavigationProps> = ({ onAddExpense }) => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Navigation items configuration
  const navItems = [
    {
      path: '/',
      label: 'Dashboard',
      icon: Home,
      description: 'Overview and analytics'
    },
    {
      path: '/expenses',
      label: 'This Month',
      icon: Receipt,
      description: 'Current month expenses'
    },
    {
      path: '/expenses/all',
      label: 'All Expenses',
      icon: BarChart3,
      description: 'Complete history'
    },
    {
      path: '/budget',
      label: 'Budget',
      icon: Wallet,
      description: 'Budget settings'
    }
  ];

  // Check if a navigation item is active
  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">💸</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">SmartSpent</h1>
              <p className="text-xs text-gray-500 hidden sm:block">
                AI Expense Tracker
              </p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors
                    ${active 
                      ? 'bg-primary-50 text-primary-700 border border-primary-200' 
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }
                  `}
                  title={item.description}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3">
            {/* Add Expense Button */}
            <button
              onClick={onAddExpense}
              className="hidden sm:flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add Expense</span>
            </button>

            {/* Mobile Add Expense Button */}
            <button
              onClick={onAddExpense}
              className="sm:hidden p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              title="Add Expense"
            >
              <Plus className="w-5 h-5" />
            </button>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              {isMobileMenuOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <div className="space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.path);
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={`
                      flex items-center space-x-3 px-4 py-3 rounded-lg text-base font-medium transition-colors
                      ${active 
                        ? 'bg-primary-50 text-primary-700 border border-primary-200' 
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                      }
                    `}
                  >
                    <Icon className="w-5 h-5" />
                    <div className="flex-1">
                      <div>{item.label}</div>
                      <div className="text-sm text-gray-500">{item.description}</div>
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};