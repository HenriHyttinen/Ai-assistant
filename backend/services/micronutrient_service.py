from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from models.micronutrients import MicronutrientGoal, DailyMicronutrientIntake, MicronutrientDeficiency
from schemas.micronutrients import (
    MicronutrientGoalCreate, MicronutrientGoalResponse,
    DailyMicronutrientIntakeCreate, DailyMicronutrientIntakeResponse,
    MicronutrientAnalysis, MicronutrientDashboard, MicronutrientDeficiencyResponse
)

class MicronutrientService:
    def __init__(self):
        # Daily recommended values for adults (can be customized per user)
        self.default_targets = {
            "vitamin_d": 15.0,  # mcg
            "vitamin_b12": 2.4,  # mcg
            "iron": 18.0,  # mg (women), 8.0 (men)
            "calcium": 1000.0,  # mg
            "magnesium": 400.0,  # mg
            "vitamin_c": 90.0,  # mg
            "folate": 400.0,  # mcg
            "zinc": 11.0,  # mg (men), 8.0 (women)
            "potassium": 3500.0,  # mg
            "fiber": 25.0,  # g
            "vitamin_a": 900.0,  # IU (men), 700.0 (women)
            "vitamin_e": 15.0,  # mg
            "vitamin_k": 120.0,  # mcg (men), 90.0 (women)
            "thiamine": 1.2,  # mg (men), 1.1 (women)
            "riboflavin": 1.3,  # mg (men), 1.1 (women)
            "niacin": 16.0,  # mg (men), 14.0 (women)
            "selenium": 55.0,  # mcg
            "phosphorus": 700.0,  # mg
            "omega_3": 1.6,  # g (men), 1.1 (women)
            "omega_6": 17.0,  # g (men), 12.0 (women)
        }

    def create_or_update_goals(self, db: Session, user_id: int, goals_data: MicronutrientGoalCreate) -> MicronutrientGoalResponse:
        """Create or update micronutrient goals for a user"""
        existing_goal = db.query(MicronutrientGoal).filter(
            and_(MicronutrientGoal.user_id == user_id, MicronutrientGoal.is_active == True)
        ).first()
        
        if existing_goal:
            # Update existing goal
            for field, value in goals_data.model_dump(exclude_unset=True).items():
                setattr(existing_goal, field, value)
            existing_goal.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_goal)
            return MicronutrientGoalResponse.model_validate(existing_goal.__dict__)
        else:
            # Create new goal with default values
            goal_dict = goals_data.model_dump(exclude_unset=True)
            
            # Fill in defaults for missing values
            for nutrient, default_value in self.default_targets.items():
                target_field = f"{nutrient}_target"
                if target_field not in goal_dict or goal_dict[target_field] is None:
                    goal_dict[target_field] = default_value
            
            goal_dict["user_id"] = user_id
            new_goal = MicronutrientGoal(**goal_dict)
            db.add(new_goal)
            db.commit()
            db.refresh(new_goal)
            return MicronutrientGoalResponse.model_validate(new_goal.__dict__)

    def get_user_goals(self, db: Session, user_id: int) -> Optional[MicronutrientGoalResponse]:
        """Get user's current micronutrient goals"""
        goal = db.query(MicronutrientGoal).filter(
            and_(MicronutrientGoal.user_id == user_id, MicronutrientGoal.is_active == True)
        ).first()
        
        if goal:
            return MicronutrientGoalResponse.model_validate(goal.__dict__)
        return None

    def log_daily_intake(self, db: Session, user_id: int, intake_data: DailyMicronutrientIntakeCreate) -> DailyMicronutrientIntakeResponse:
        """Log daily micronutrient intake"""
        # Check if intake already exists for this date
        existing_intake = db.query(DailyMicronutrientIntake).filter(
            and_(
                DailyMicronutrientIntake.user_id == user_id,
                func.date(DailyMicronutrientIntake.date) == intake_data.date.date()
            )
        ).first()
        
        if existing_intake:
            # Update existing intake
            for field, value in intake_data.model_dump(exclude_unset=True).items():
                if field != "date":  # Don't update the date
                    setattr(existing_intake, field, value)
            existing_intake.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_intake)
            return DailyMicronutrientIntakeResponse.model_validate(existing_intake.__dict__)
        else:
            # Create new intake
            intake_dict = intake_data.model_dump()
            intake_dict["user_id"] = user_id
            new_intake = DailyMicronutrientIntake(**intake_dict)
            db.add(new_intake)
            db.commit()
            db.refresh(new_intake)
            return DailyMicronutrientIntakeResponse.model_validate(new_intake.__dict__)

    def get_daily_intake(self, db: Session, user_id: int, date: datetime) -> Optional[DailyMicronutrientIntakeResponse]:
        """Get daily micronutrient intake for a specific date"""
        intake = db.query(DailyMicronutrientIntake).filter(
            and_(
                DailyMicronutrientIntake.user_id == user_id,
                func.date(DailyMicronutrientIntake.date) == date.date()
            )
        ).first()
        
        if intake:
            return DailyMicronutrientIntakeResponse.model_validate(intake.__dict__)
        return None

    def get_weekly_average(self, db: Session, user_id: int, start_date: datetime) -> Dict[str, float]:
        """Get weekly average micronutrient intake"""
        end_date = start_date + timedelta(days=7)
        
        intakes = db.query(DailyMicronutrientIntake).filter(
            and_(
                DailyMicronutrientIntake.user_id == user_id,
                DailyMicronutrientIntake.date >= start_date,
                DailyMicronutrientIntake.date < end_date
            )
        ).all()
        
        if not intakes:
            return {}
        
        # Calculate averages
        micronutrients = [
            "vitamin_d", "vitamin_b12", "iron", "calcium", "magnesium",
            "vitamin_c", "folate", "zinc", "potassium", "fiber",
            "vitamin_a", "vitamin_e", "vitamin_k", "thiamine", "riboflavin",
            "niacin", "selenium", "phosphorus", "omega_3", "omega_6"
        ]
        
        averages = {}
        for nutrient in micronutrients:
            total = sum(getattr(intake, f"{nutrient}_intake", 0) for intake in intakes)
            averages[nutrient] = total / len(intakes)
        
        return averages

    def analyze_deficiencies(self, db: Session, user_id: int, current_intake: Dict[str, float]) -> List[MicronutrientDeficiencyResponse]:
        """Analyze micronutrient deficiencies based on current intake"""
        goals = self.get_user_goals(db, user_id)
        if not goals:
            return []
        
        deficiencies = []
        micronutrients = [
            "vitamin_d", "vitamin_b12", "iron", "calcium", "magnesium",
            "vitamin_c", "folate", "zinc", "potassium", "fiber"
        ]
        
        for nutrient in micronutrients:
            current = current_intake.get(nutrient, 0)
            target = getattr(goals, f"{nutrient}_target", 0)
            
            if target > 0 and current < target:
                deficiency_percentage = ((target - current) / target) * 100
                
                # Determine deficiency level
                if deficiency_percentage >= 50:
                    level = "severe"
                elif deficiency_percentage >= 25:
                    level = "moderate"
                else:
                    level = "mild"
                
                # Check if deficiency already exists
                existing = db.query(MicronutrientDeficiency).filter(
                    and_(
                        MicronutrientDeficiency.user_id == user_id,
                        MicronutrientDeficiency.micronutrient_name == nutrient,
                        MicronutrientDeficiency.is_resolved == False
                    )
                ).first()
                
                if existing:
                    # Update existing deficiency
                    existing.deficiency_level = level
                    existing.current_intake = current
                    existing.deficiency_percentage = deficiency_percentage
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new deficiency
                    food_suggestions = self._get_food_suggestions(nutrient)
                    supplement_suggestions = self._get_supplement_suggestions(nutrient)
                    
                    deficiency = MicronutrientDeficiency(
                        user_id=user_id,
                        micronutrient_name=nutrient,
                        deficiency_level=level,
                        current_intake=current,
                        recommended_intake=target,
                        deficiency_percentage=deficiency_percentage,
                        food_suggestions=json.dumps(food_suggestions),
                        supplement_suggestions=supplement_suggestions
                    )
                    db.add(deficiency)
                
                deficiencies.append(MicronutrientDeficiencyResponse(
                    id=existing.id if existing else 0,
                    user_id=user_id,
                    micronutrient_name=nutrient,
                    deficiency_level=level,
                    current_intake=current,
                    recommended_intake=target,
                    deficiency_percentage=deficiency_percentage,
                    food_suggestions=json.dumps(food_suggestions) if not existing else existing.food_suggestions,
                    supplement_suggestions=supplement_suggestions if not existing else existing.supplement_suggestions,
                    is_resolved=False,
                    resolved_at=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ))
        
        db.commit()
        return deficiencies

    def get_dashboard(self, db: Session, user_id: int) -> MicronutrientDashboard:
        """Get micronutrient dashboard data"""
        goals = self.get_user_goals(db, user_id)
        if not goals:
            # Create default goals if none exist
            goals = self.create_or_update_goals(db, user_id, MicronutrientGoalCreate())
        
        today = datetime.utcnow().date()
        today_intake = self.get_daily_intake(db, user_id, datetime.combine(today, datetime.min.time()))
        
        # Get weekly average
        week_start = today - timedelta(days=today.weekday())
        weekly_average = self.get_weekly_average(db, user_id, datetime.combine(week_start, datetime.min.time()))
        
        # Analyze deficiencies
        current_intake = today_intake.model_dump() if today_intake else {}
        deficiencies = self.analyze_deficiencies(db, user_id, current_intake)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(goals, current_intake)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(deficiencies, weekly_average)
        
        # Get trend data for charts
        trend_data = self._get_trend_data(db, user_id, 30)  # Last 30 days
        
        return MicronutrientDashboard(
            current_goals=goals,
            today_intake=today_intake,
            weekly_average=weekly_average,
            deficiencies=deficiencies,
            recommendations=recommendations,
            overall_score=overall_score,
            trend_data=trend_data
        )

    def _get_food_suggestions(self, nutrient: str) -> List[str]:
        """Get food suggestions for a specific nutrient"""
        suggestions = {
            "vitamin_d": ["Fatty fish (salmon, mackerel)", "Fortified dairy products", "Egg yolks", "Mushrooms"],
            "vitamin_b12": ["Meat", "Fish", "Dairy products", "Fortified cereals"],
            "iron": ["Red meat", "Spinach", "Lentils", "Fortified cereals", "Dark chocolate"],
            "calcium": ["Dairy products", "Leafy greens", "Sardines", "Almonds", "Fortified foods"],
            "magnesium": ["Nuts and seeds", "Leafy greens", "Whole grains", "Dark chocolate", "Avocados"],
            "vitamin_c": ["Citrus fruits", "Bell peppers", "Strawberries", "Broccoli", "Kiwi"],
            "folate": ["Leafy greens", "Legumes", "Fortified grains", "Asparagus", "Avocados"],
            "zinc": ["Meat", "Shellfish", "Nuts and seeds", "Dairy products", "Whole grains"],
            "potassium": ["Bananas", "Sweet potatoes", "Spinach", "Beans", "Avocados"],
            "fiber": ["Whole grains", "Fruits", "Vegetables", "Legumes", "Nuts and seeds"]
        }
        return suggestions.get(nutrient, [])

    def _get_supplement_suggestions(self, nutrient: str) -> str:
        """Get supplement suggestions for a specific nutrient"""
        suggestions = {
            "vitamin_d": "Consider Vitamin D3 supplement, especially in winter months",
            "vitamin_b12": "B12 supplement or sublingual tablets if vegetarian/vegan",
            "iron": "Iron supplement with vitamin C for better absorption",
            "calcium": "Calcium supplement with vitamin D for better absorption",
            "magnesium": "Magnesium glycinate or citrate supplement",
            "vitamin_c": "Vitamin C supplement or multivitamin",
            "folate": "Folate or folic acid supplement",
            "zinc": "Zinc supplement, especially during cold season",
            "potassium": "Potassium supplement (consult doctor first)",
            "fiber": "Psyllium husk or other fiber supplements"
        }
        return suggestions.get(nutrient, "Consider consulting a healthcare provider")

    def _calculate_overall_score(self, goals, current_intake: Dict[str, float]) -> float:
        """Calculate overall micronutrient adequacy score (0-100)"""
        micronutrients = [
            "vitamin_d", "vitamin_b12", "iron", "calcium", "magnesium",
            "vitamin_c", "folate", "zinc", "potassium", "fiber"
        ]
        
        total_score = 0
        valid_nutrients = 0
        
        for nutrient in micronutrients:
            current = current_intake.get(nutrient, 0)
            target = getattr(goals, f"{nutrient}_target", 0)
            
            if target > 0:
                score = min(100, (current / target) * 100)
                total_score += score
                valid_nutrients += 1
        
        return total_score / valid_nutrients if valid_nutrients > 0 else 0

    def _generate_recommendations(self, deficiencies: List, weekly_average: Dict[str, float]) -> List[str]:
        """Generate personalized recommendations based on deficiencies and intake"""
        recommendations = []
        
        if not deficiencies:
            recommendations.append("Great job! You're meeting all your micronutrient targets.")
        else:
            for deficiency in deficiencies:
                if deficiency.deficiency_level == "severe":
                    recommendations.append(f"Priority: Address {deficiency.micronutrient_name} deficiency - consider supplements")
                elif deficiency.deficiency_level == "moderate":
                    recommendations.append(f"Focus on increasing {deficiency.micronutrient_name} intake through diet")
                else:
                    recommendations.append(f"Minor {deficiency.micronutrient_name} deficiency - small dietary adjustments needed")
        
        # Add general recommendations based on weekly averages
        if weekly_average.get("fiber", 0) < 20:
            recommendations.append("Increase fiber intake with more whole grains and vegetables")
        
        if weekly_average.get("vitamin_c", 0) < 60:
            recommendations.append("Add more citrus fruits and vegetables to boost vitamin C")
        
        return recommendations

    def _get_trend_data(self, db: Session, user_id: int, days: int) -> List[Dict[str, Any]]:
        """Get trend data for charts"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        intakes = db.query(DailyMicronutrientIntake).filter(
            and_(
                DailyMicronutrientIntake.user_id == user_id,
                DailyMicronutrientIntake.date >= start_date,
                DailyMicronutrientIntake.date <= end_date
            )
        ).order_by(DailyMicronutrientIntake.date).all()
        
        trend_data = []
        for intake in intakes:
            trend_data.append({
                "date": intake.date.isoformat(),
                "vitamin_d": intake.vitamin_d_intake,
                "vitamin_b12": intake.vitamin_b12_intake,
                "iron": intake.iron_intake,
                "calcium": intake.calcium_intake,
                "magnesium": intake.magnesium_intake,
                "vitamin_c": intake.vitamin_c_intake,
                "folate": intake.folate_intake,
                "zinc": intake.zinc_intake,
                "potassium": intake.potassium_intake,
                "fiber": intake.fiber_intake
            })
        
        return trend_data