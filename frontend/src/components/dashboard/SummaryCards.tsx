import React from 'react';
import { TrendingUp, TrendingDown, Target, PiggyBank } from 'lucide-react';
import type { DashboardSummary } from '../../types';

// Props for summary cards component
interface SummaryCardsProps {
  data: DashboardSummary;
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({ data }) => {
  const {
    total_spent,
    total_budget,
    budget_utilization,
    savings,
    savings_rate
  } = data;

  // Card data configuration
  const cards = [
    {
      title: 'Total Spent',
      value: `₹${total_spent.toLocaleString()}`,
      subtitle: `of ₹${total_budget.toLocaleString()} budget`,
      icon: Target,
      color: budget_utilization >= 100 ? 'text-red-600' : 
             budget_utilization >= 80 ? 'text-yellow-600' : 'text-green-600',
      bgColor: budget_utilization >= 100 ? 'bg-red-50' : 
               budget_utilization >= 80 ? 'bg-yellow-50' : 'bg-green-50'
    },
    {
      title: 'Budget Used',
      value: `${budget_utilization.toFixed(1)}%`,
      subtitle: `${(100 - budget_utilization).toFixed(1)}% remaining`,
      icon: TrendingUp,
      color: budget_utilization >= 100 ? 'text-red-600' : 
             budget_utilization >= 80 ? 'text-yellow-600' : 'text-green-600',
      bgColor: budget_utilization >= 100 ? 'bg-red-50' : 
               budget_utilization >= 80 ? 'bg-yellow-50' : 'bg-green-50'
    },
    {
      title: 'Savings',
      value: `₹${savings.toLocaleString()}`,
      subtitle: `${savings_rate.toFixed(1)}% of income`,
      icon: PiggyBank,
      color: savings >= 0 ? 'text-green-600' : 'text-red-600',
      bgColor: savings >= 0 ? 'bg-green-50' : 'bg-red-50'
    },
    {
      title: 'Trend',
      value: savings_rate >= 0 ? 'Positive' : 'Negative',
      subtitle: `${Math.abs(savings_rate).toFixed(1)}% ${savings_rate >= 0 ? 'saved' : 'overspent'}`,
      icon: savings_rate >= 0 ? TrendingUp : TrendingDown,
      color: savings_rate >= 0 ? 'text-green-600' : 'text-red-600',
      bgColor: savings_rate >= 0 ? 'bg-green-50' : 'bg-red-50'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {cards.map((card, index) => {
        const IconComponent = card.icon;
        
        return (
          <div
            key={index}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200"
          >
            <div className="flex items-center justify-between">
              <div>
                {/* Card title */}
                <p className="text-sm font-medium text-gray-600 mb-1">
                  {card.title}
                </p>
                
                {/* Main value */}
                <p className={`text-2xl font-bold ${card.color} mb-1`}>
                  {card.value}
                </p>
                
                {/* Subtitle */}
                <p className="text-sm text-gray-500">
                  {card.subtitle}
                </p>
              </div>
              
              {/* Icon with background */}
              <div className={`p-3 rounded-full ${card.bgColor}`}>
                <IconComponent className={`w-6 h-6 ${card.color}`} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};