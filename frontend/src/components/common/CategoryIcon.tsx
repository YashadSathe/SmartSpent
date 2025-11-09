import React from 'react';
import { 
  Utensils, 
  Coffee, 
  Car, 
  ShoppingBag, 
  Film, 
  Receipt, 
  Heart, 
  Book, 
  Plane, 
  ShoppingCart, 
  Scissors,
  Circle 
} from 'lucide-react';

// Icon mapping for each expense category
const CATEGORY_ICONS: { [key: string]: React.ComponentType<any> } = {
  Food: Utensils,
  Drinks: Coffee,
  Transport: Car,
  Shopping: ShoppingBag,
  Entertainment: Film,
  Bills: Receipt,
  Healthcare: Heart,
  Education: Book,
  Travel: Plane,
  Groceries: ShoppingCart,
  'Personal Care': Scissors,
  Other: Circle
};

// Props for the category icon component
interface CategoryIconProps {
  category: string;
  size?: number;
  className?: string;
}

export const CategoryIcon: React.FC<CategoryIconProps> = ({ 
  category, 
  size = 20, 
  className = '' 
}) => {
  // Get the appropriate icon for the category, fallback to Circle for unknown categories
  const IconComponent = CATEGORY_ICONS[category] || Circle;

  return (
    <div className={`inline-flex items-center justify-center ${className}`}>
      <IconComponent size={size} />
    </div>
  );
};