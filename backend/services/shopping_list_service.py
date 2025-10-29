"""
Service for generating shopping lists from meal plans and individual meals
"""

from sqlalchemy.orm import Session
from models.nutrition import MealPlan, MealPlanMeal, ShoppingList, ShoppingListItem
from models.recipe import Ingredient
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

class ShoppingListService:
    """Service for generating and managing shopping lists from meal plans"""
    
    def __init__(self):
        pass
    
    def generate_shopping_list_from_meal_plan(self, db: Session, user_id: int, 
                                            meal_plan_id: str, list_name: Optional[str] = None) -> ShoppingList:
        """
        Generate a shopping list from all meals in a meal plan
        """
        try:
            # Get the meal plan
            meal_plan = db.query(MealPlan).filter(
                MealPlan.id == meal_plan_id,
                MealPlan.user_id == user_id
            ).first()
            
            if not meal_plan:
                raise ValueError(f"Meal plan {meal_plan_id} not found")
            
            # Get all meals from the meal plan
            meals = db.query(MealPlanMeal).filter(
                MealPlanMeal.meal_plan_id == meal_plan_id
            ).all()
            
            if not meals:
                raise ValueError(f"No meals found in meal plan {meal_plan_id}")
            
            # Generate shopping list name if not provided
            if not list_name:
                list_name = f"Shopping List - {meal_plan.start_date.strftime('%Y-%m-%d')}"
                if meal_plan.end_date and meal_plan.end_date != meal_plan.start_date:
                    list_name += f" to {meal_plan.end_date.strftime('%Y-%m-%d')}"
            
            # Create shopping list
            shopping_list = ShoppingList(
                id=f"sl_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                user_id=user_id,
                meal_plan_id=meal_plan_id,
                list_name=list_name,
                is_active=True
            )
            
            db.add(shopping_list)
            db.flush()
            
            # Extract and aggregate ingredients from all meals
            aggregated_ingredients = self._extract_ingredients_from_meals(meals)
            
            # Create shopping list items
            for ingredient_data in aggregated_ingredients:
                item = ShoppingListItem(
                    shopping_list_id=shopping_list.id,
                    ingredient_id=ingredient_data['ingredient_id'],
                    quantity=ingredient_data['total_quantity'],
                    unit=ingredient_data['unit'],
                    category=ingredient_data['category'],
                    notes=ingredient_data.get('notes', '')
                )
                db.add(item)
            
            db.commit()
            db.refresh(shopping_list)
            
            logger.info(f"Generated shopping list {shopping_list.id} with {len(aggregated_ingredients)} items")
            return shopping_list
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error generating shopping list from meal plan: {str(e)}")
            raise
    
    def generate_shopping_list_from_meal(self, db: Session, user_id: int, 
                                       meal_id: str, list_name: Optional[str] = None) -> ShoppingList:
        """
        Generate a shopping list from a single meal
        """
        try:
            # Get the meal
            meal = db.query(MealPlanMeal).filter(
                MealPlanMeal.id == meal_id
            ).first()
            
            if not meal:
                raise ValueError(f"Meal {meal_id} not found")
            
            # Verify the meal belongs to the user
            meal_plan = db.query(MealPlan).filter(
                MealPlan.id == meal.meal_plan_id,
                MealPlan.user_id == user_id
            ).first()
            
            if not meal_plan:
                raise ValueError(f"Meal {meal_id} does not belong to user {user_id}")
            
            # Generate shopping list name if not provided
            if not list_name:
                list_name = f"Shopping List - {meal.meal_name} ({meal.meal_type})"
            
            # Create shopping list
            shopping_list = ShoppingList(
                id=f"sl_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                user_id=user_id,
                meal_plan_id=meal.meal_plan_id,
                list_name=list_name,
                is_active=True
            )
            
            db.add(shopping_list)
            db.flush()
            
            # Extract ingredients from the single meal
            aggregated_ingredients = self._extract_ingredients_from_meals([meal])
            
            # Create shopping list items
            for ingredient_data in aggregated_ingredients:
                item = ShoppingListItem(
                    shopping_list_id=shopping_list.id,
                    ingredient_id=ingredient_data['ingredient_id'],
                    quantity=ingredient_data['total_quantity'],
                    unit=ingredient_data['unit'],
                    category=ingredient_data['category'],
                    notes=ingredient_data.get('notes', '')
                )
                db.add(item)
            
            db.commit()
            db.refresh(shopping_list)
            
            logger.info(f"Generated shopping list {shopping_list.id} with {len(aggregated_ingredients)} items from meal {meal_id}")
            return shopping_list
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error generating shopping list from meal: {str(e)}")
            raise
    
    def generate_shopping_list_from_meal_types(self, db: Session, user_id: int, 
                                             meal_plan_id: str, meal_types: List[str],
                                             list_name: Optional[str] = None) -> ShoppingList:
        """
        Generate a shopping list from specific meal types in a meal plan
        """
        try:
            # Get the meal plan
            meal_plan = db.query(MealPlan).filter(
                MealPlan.id == meal_plan_id,
                MealPlan.user_id == user_id
            ).first()
            
            if not meal_plan:
                raise ValueError(f"Meal plan {meal_plan_id} not found")
            
            # Get meals of specified types
            meals = db.query(MealPlanMeal).filter(
                MealPlanMeal.meal_plan_id == meal_plan_id,
                MealPlanMeal.meal_type.in_(meal_types)
            ).all()
            
            if not meals:
                raise ValueError(f"No meals of types {meal_types} found in meal plan {meal_plan_id}")
            
            # Generate shopping list name if not provided
            if not list_name:
                meal_types_str = ", ".join(meal_types)
                list_name = f"Shopping List - {meal_types_str} ({meal_plan.start_date.strftime('%Y-%m-%d')})"
            
            # Create shopping list
            shopping_list = ShoppingList(
                id=f"sl_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                user_id=user_id,
                meal_plan_id=meal_plan_id,
                list_name=list_name,
                is_active=True
            )
            
            db.add(shopping_list)
            db.flush()
            
            # Extract and aggregate ingredients from filtered meals
            aggregated_ingredients = self._extract_ingredients_from_meals(meals)
            
            # Create shopping list items
            for ingredient_data in aggregated_ingredients:
                item = ShoppingListItem(
                    shopping_list_id=shopping_list.id,
                    ingredient_id=ingredient_data['ingredient_id'],
                    quantity=ingredient_data['total_quantity'],
                    unit=ingredient_data['unit'],
                    category=ingredient_data['category'],
                    notes=ingredient_data.get('notes', '')
                )
                db.add(item)
            
            db.commit()
            db.refresh(shopping_list)
            
            logger.info(f"Generated shopping list {shopping_list.id} with {len(aggregated_ingredients)} items for meal types {meal_types}")
            return shopping_list
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error generating shopping list from meal types: {str(e)}")
            raise
    
    def _extract_ingredients_from_meals(self, meals: List[MealPlanMeal]) -> List[Dict[str, Any]]:
        """
        Extract and aggregate ingredients from a list of meals
        """
        ingredient_aggregator = defaultdict(lambda: {
            'total_quantity': 0,
            'unit': '',
            'category': '',
            'ingredient_id': '',
            'ingredient_name': '',
            'meals_used_in': []
        })
        
        for meal in meals:
            # Extract ingredients from recipe_details if available
            if meal.recipe_details and isinstance(meal.recipe_details, dict):
                ingredients = meal.recipe_details.get('ingredients', [])
                
                for ingredient in ingredients:
                    if isinstance(ingredient, dict) and 'name' in ingredient:
                        ingredient_name = ingredient['name'].lower().strip()
                        quantity = float(ingredient.get('quantity', 0))
                        unit = ingredient.get('unit', 'g')
                        
                        # Use ingredient name as ID for now (in a real system, you'd have proper ingredient IDs)
                        ingredient_id = f"ing_{ingredient_name.replace(' ', '_')}"
                        
                        if ingredient_id in ingredient_aggregator:
                            # Aggregate quantities
                            ingredient_aggregator[ingredient_id]['total_quantity'] += quantity
                            ingredient_aggregator[ingredient_id]['meals_used_in'].append(meal.meal_name)
                        else:
                            # First occurrence
                            ingredient_aggregator[ingredient_id] = {
                                'ingredient_id': ingredient_id,
                                'ingredient_name': ingredient['name'],
                                'total_quantity': quantity,
                                'unit': unit,
                                'category': self._categorize_ingredient(ingredient['name']),
                                'meals_used_in': [meal.meal_name]
                            }
        
        # Convert to list and add notes about usage
        result = []
        for ingredient_data in ingredient_aggregator.values():
            if ingredient_data['total_quantity'] > 0:
                # Add notes about which meals use this ingredient
                meals_str = ", ".join(ingredient_data['meals_used_in'])
                ingredient_data['notes'] = f"Used in: {meals_str}"
                result.append(ingredient_data)
        
        return result
    
    def _categorize_ingredient(self, ingredient_name: str) -> str:
        """
        Categorize an ingredient into food groups
        """
        ingredient_lower = ingredient_name.lower()
        
        # Protein sources
        protein_keywords = ['chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'turkey', 'lamb', 'eggs', 'tofu', 'beans', 'lentils', 'chickpeas', 'quinoa', 'tempeh', 'seitan']
        if any(keyword in ingredient_lower for keyword in protein_keywords):
            return 'protein'
        
        # Dairy
        dairy_keywords = ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'sour cream', 'cottage cheese', 'mozzarella', 'cheddar', 'parmesan', 'feta']
        if any(keyword in ingredient_lower for keyword in dairy_keywords):
            return 'dairy'
        
        # Vegetables
        vegetable_keywords = ['tomato', 'onion', 'garlic', 'carrot', 'celery', 'bell pepper', 'broccoli', 'spinach', 'lettuce', 'cucumber', 'zucchini', 'eggplant', 'mushroom', 'potato', 'sweet potato']
        if any(keyword in ingredient_lower for keyword in vegetable_keywords):
            return 'vegetables'
        
        # Fruits
        fruit_keywords = ['apple', 'banana', 'orange', 'lemon', 'lime', 'berry', 'strawberry', 'blueberry', 'raspberry', 'grape', 'avocado', 'mango', 'pineapple']
        if any(keyword in ingredient_lower for keyword in fruit_keywords):
            return 'fruits'
        
        # Grains and carbs
        grain_keywords = ['rice', 'pasta', 'bread', 'flour', 'oats', 'quinoa', 'barley', 'wheat', 'corn', 'tortilla', 'noodles']
        if any(keyword in ingredient_lower for keyword in grain_keywords):
            return 'grains'
        
        # Nuts and seeds
        nut_keywords = ['almond', 'walnut', 'peanut', 'cashew', 'pistachio', 'sunflower seed', 'chia seed', 'flax seed', 'sesame seed']
        if any(keyword in ingredient_lower for keyword in nut_keywords):
            return 'nuts_seeds'
        
        # Oils and fats
        oil_keywords = ['oil', 'olive oil', 'coconut oil', 'butter', 'ghee', 'avocado oil', 'sesame oil']
        if any(keyword in ingredient_lower for keyword in oil_keywords):
            return 'oils_fats'
        
        # Herbs and spices
        herb_keywords = ['salt', 'pepper', 'basil', 'oregano', 'thyme', 'rosemary', 'parsley', 'cilantro', 'ginger', 'garlic', 'onion powder', 'paprika', 'cumin', 'cinnamon', 'vanilla']
        if any(keyword in ingredient_lower for keyword in herb_keywords):
            return 'herbs_spices'
        
        # Condiments and sauces
        condiment_keywords = ['sauce', 'vinegar', 'soy sauce', 'hot sauce', 'ketchup', 'mustard', 'mayonnaise', 'salsa', 'pesto']
        if any(keyword in ingredient_lower for keyword in condiment_keywords):
            return 'condiments'
        
        # Default category
        return 'other'
    
    def get_shopping_list_summary(self, db: Session, shopping_list_id: str) -> Dict[str, Any]:
        """
        Get a summary of a shopping list with categorized items
        """
        try:
            shopping_list = db.query(ShoppingList).filter(
                ShoppingList.id == shopping_list_id
            ).first()
            
            if not shopping_list:
                raise ValueError(f"Shopping list {shopping_list_id} not found")
            
            # Group items by category
            categories = defaultdict(list)
            total_items = 0
            purchased_items = 0
            
            for item in shopping_list.items:
                categories[item.category].append({
                    'id': item.id,
                    'ingredient_id': item.ingredient_id,
                    'quantity': item.quantity,
                    'unit': item.unit,
                    'is_purchased': item.is_purchased,
                    'notes': item.notes
                })
                total_items += 1
                if item.is_purchased:
                    purchased_items += 1
            
            return {
                'shopping_list_id': shopping_list.id,
                'list_name': shopping_list.list_name,
                'meal_plan_id': shopping_list.meal_plan_id,
                'total_items': total_items,
                'purchased_items': purchased_items,
                'completion_percentage': (purchased_items / total_items * 100) if total_items > 0 else 0,
                'categories': dict(categories),
                'created_at': shopping_list.created_at,
                'updated_at': shopping_list.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting shopping list summary: {str(e)}")
            raise
    
    def update_shopping_list_item_quantity(self, db: Session, user_id: int, 
                                         item_id: int, new_quantity: float) -> Dict[str, Any]:
        """
        Update the quantity of a shopping list item
        """
        try:
            # Get the shopping list item and verify ownership
            item = db.query(ShoppingListItem).join(ShoppingList).filter(
                ShoppingListItem.id == item_id,
                ShoppingList.user_id == user_id
            ).first()
            
            if not item:
                raise ValueError(f"Shopping list item {item_id} not found or doesn't belong to user")
            
            if new_quantity <= 0:
                raise ValueError("Quantity must be greater than 0")
            
            # Update the quantity
            old_quantity = item.quantity
            item.quantity = new_quantity
            
            db.commit()
            db.refresh(item)
            
            logger.info(f"Updated item {item_id} quantity from {old_quantity} to {new_quantity}")
            
            return {
                "message": "Item quantity updated successfully",
                "item_id": item.id,
                "old_quantity": old_quantity,
                "new_quantity": item.quantity,
                "unit": item.unit
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating shopping list item quantity: {str(e)}")
            raise
    
    def remove_shopping_list_item(self, db: Session, user_id: int, item_id: int) -> Dict[str, Any]:
        """
        Remove an item from a shopping list
        """
        try:
            # Get the shopping list item and verify ownership
            item = db.query(ShoppingListItem).join(ShoppingList).filter(
                ShoppingListItem.id == item_id,
                ShoppingList.user_id == user_id
            ).first()
            
            if not item:
                raise ValueError(f"Shopping list item {item_id} not found or doesn't belong to user")
            
            # Store item details for response
            item_details = {
                "id": item.id,
                "ingredient_id": item.ingredient_id,
                "quantity": item.quantity,
                "unit": item.unit,
                "category": item.category
            }
            
            # Remove the item
            db.delete(item)
            db.commit()
            
            logger.info(f"Removed item {item_id} from shopping list")
            
            return {
                "message": "Item removed successfully",
                "removed_item": item_details
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error removing shopping list item: {str(e)}")
            raise
    
    def toggle_item_purchased_status(self, db: Session, user_id: int, 
                                   item_id: int) -> Dict[str, Any]:
        """
        Toggle the purchased status of a shopping list item
        """
        try:
            # Get the shopping list item and verify ownership
            item = db.query(ShoppingListItem).join(ShoppingList).filter(
                ShoppingListItem.id == item_id,
                ShoppingList.user_id == user_id
            ).first()
            
            if not item:
                raise ValueError(f"Shopping list item {item_id} not found or doesn't belong to user")
            
            # Toggle the purchased status
            old_status = item.is_purchased
            item.is_purchased = not item.is_purchased
            
            db.commit()
            db.refresh(item)
            
            logger.info(f"Toggled item {item_id} purchased status from {old_status} to {item.is_purchased}")
            
            return {
                "message": "Item purchased status updated successfully",
                "item_id": item.id,
                "old_status": old_status,
                "new_status": item.is_purchased
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error toggling item purchased status: {str(e)}")
            raise
    
    def add_custom_item_to_shopping_list(self, db: Session, user_id: int, 
                                       shopping_list_id: str, item_name: str, 
                                       quantity: float, unit: str, 
                                       category: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a custom item to an existing shopping list
        """
        try:
            # Verify shopping list ownership
            shopping_list = db.query(ShoppingList).filter(
                ShoppingList.id == shopping_list_id,
                ShoppingList.user_id == user_id
            ).first()
            
            if not shopping_list:
                raise ValueError(f"Shopping list {shopping_list_id} not found or doesn't belong to user")
            
            # Auto-categorize if not provided
            if not category:
                category = self._categorize_ingredient(item_name)
            
            # Create ingredient ID from name
            ingredient_id = f"custom_{item_name.lower().replace(' ', '_')}"
            
            # Create new shopping list item
            new_item = ShoppingListItem(
                shopping_list_id=shopping_list_id,
                ingredient_id=ingredient_id,
                quantity=quantity,
                unit=unit,
                category=category,
                notes=f"Custom item: {item_name}"
            )
            
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            
            logger.info(f"Added custom item '{item_name}' to shopping list {shopping_list_id}")
            
            return {
                "message": "Custom item added successfully",
                "item": {
                    "id": new_item.id,
                    "ingredient_id": new_item.ingredient_id,
                    "quantity": new_item.quantity,
                    "unit": new_item.unit,
                    "category": new_item.category,
                    "notes": new_item.notes
                }
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding custom item to shopping list: {str(e)}")
            raise
    
    def update_item_notes(self, db: Session, user_id: int, item_id: int, 
                         notes: str) -> Dict[str, Any]:
        """
        Update the notes for a shopping list item
        """
        try:
            # Get the shopping list item and verify ownership
            item = db.query(ShoppingListItem).join(ShoppingList).filter(
                ShoppingListItem.id == item_id,
                ShoppingList.user_id == user_id
            ).first()
            
            if not item:
                raise ValueError(f"Shopping list item {item_id} not found or doesn't belong to user")
            
            # Update the notes
            old_notes = item.notes
            item.notes = notes
            
            db.commit()
            db.refresh(item)
            
            logger.info(f"Updated item {item_id} notes")
            
            return {
                "message": "Item notes updated successfully",
                "item_id": item.id,
                "old_notes": old_notes,
                "new_notes": item.notes
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating item notes: {str(e)}")
            raise
