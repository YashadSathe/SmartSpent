import React from 'react';

// Confidence badge to show AI prediction confidence with color coding
interface ConfidenceBadgeProps {
  confidence: number;
  showLabel?: boolean;
  size?: 'sm' | 'md';
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ 
  confidence, 
  showLabel = true,
  size = 'md'
}) => {
  // Determine color based on confidence level
  const getColorClass = (conf: number): string => {
    if (conf >= 0.9) return 'bg-green-100 text-green-800 border-green-200';    // High confidence - green
    if (conf >= 0.7) return 'bg-yellow-100 text-yellow-800 border-yellow-200'; // Medium confidence - yellow
    return 'bg-red-100 text-red-800 border-red-200';                           // Low confidence - red
  };

  const getSizeClass = (size: 'sm' | 'md'): string => {
    return size === 'sm' ? 'px-2 py-1 text-xs' : 'px-3 py-1 text-sm';
  };

  const percentage = Math.round(confidence * 100);

  return (
    <span 
      className={`
        inline-flex items-center font-medium rounded-full border
        ${getColorClass(confidence)} 
        ${getSizeClass(size)}
      `}
    >
      {/* Confidence indicator dot */}
      <span 
        className={`w-2 h-2 rounded-full mr-1 ${
          confidence >= 0.9 ? 'bg-green-500' :
          confidence >= 0.7 ? 'bg-yellow-500' : 'bg-red-500'
        }`}
      ></span>
      
      {/* Confidence percentage */}
      {showLabel ? `${percentage}% confident` : `${percentage}%`}
    </span>
  );
};