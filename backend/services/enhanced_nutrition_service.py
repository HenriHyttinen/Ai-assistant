from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from typing import List, Optional, Dict, Any, Tuple
import json
from datetime import datetime, date, timedelta
import statistics

from models.enhanced_nutrition import (
    NutritionalProfile, DailyNutritionalIntake, FoodComposition,
    NutritionalAnalysis, HealthMetrics, NutritionalCorrelation
)
from schemas.enhanced_nutrition import (
    NutritionalProfileCreate, NutritionalProfileUpdate, NutritionalProfileSearch,
    DailyNutritionalIntakeCreate, DailyNutritionalIntakeUpdate,
    FoodCompositionCreate, FoodCompositionUpdate, FoodCompositionSearch,
    NutritionalAnalysisCreate, NutritionalAnalysisUpdate, NutritionalAnalysisSearch,
    HealthMetricsCreate, HealthMetricsUpdate,
    NutritionalCorrelationCreate, NutritionalDashboard, NutritionalInsights
)

class EnhancedNutritionService:
    def __init__(self, db: Session):
        self.db = db

    # Nutritional Profile Methods
    def create_nutritional_profile(self, user_id: str, profile_data: NutritionalProfileCreate) -> NutritionalProfile:
        """Create a new nutritional profile for a user"""
        # If this is set as default, unset other default profiles
        if profile_data.is_default:
            self.db.query(NutritionalProfile).filter(
                and_(
                    NutritionalProfile.user_id == user_id,
                    NutritionalProfile.is_default == True
                )
            ).update({"is_default": False})
        
        profile = NutritionalProfile(
            user_id=user_id,
            profile_name=profile_data.profile_name,
            is_default=profile_data.is_default,
            daily_calories=profile_data.daily_calories,
            protein_grams=profile_data.protein_grams,
            carbs_grams=profile_data.carbs_grams,
            fat_grams=profile_data.fat_grams,
            fiber_grams=profile_data.fiber_grams,
            sugar_grams=profile_data.sugar_grams,
            sodium_mg=profile_data.sodium_mg,
            # Advanced macronutrients
            saturated_fat_grams=profile_data.saturated_fat_grams,
            monounsaturated_fat_grams=profile_data.monounsaturated_fat_grams,
            polyunsaturated_fat_grams=profile_data.polyunsaturated_fat_grams,
            trans_fat_grams=profile_data.trans_fat_grams,
            cholesterol_mg=profile_data.cholesterol_mg,
            # Carbohydrate breakdown
            total_carbs_grams=profile_data.total_carbs_grams,
            net_carbs_grams=profile_data.net_carbs_grams,
            simple_carbs_grams=profile_data.simple_carbs_grams,
            complex_carbs_grams=profile_data.complex_carbs_grams,
            starch_grams=profile_data.starch_grams,
            # Micronutrients
            vitamin_a_mcg=profile_data.vitamin_a_mcg,
            vitamin_c_mg=profile_data.vitamin_c_mg,
            vitamin_d_mcg=profile_data.vitamin_d_mcg,
            vitamin_e_mg=profile_data.vitamin_e_mg,
            vitamin_k_mcg=profile_data.vitamin_k_mcg,
            thiamine_mg=profile_data.thiamine_mg,
            riboflavin_mg=profile_data.riboflavin_mg,
            niacin_mg=profile_data.niacin_mg,
            pantothenic_acid_mg=profile_data.pantothenic_acid_mg,
            pyridoxine_mg=profile_data.pyridoxine_mg,
            biotin_mcg=profile_data.biotin_mcg,
            folate_mcg=profile_data.folate_mcg,
            cobalamin_mcg=profile_data.cobalamin_mcg,
            # Minerals
            calcium_mg=profile_data.calcium_mg,
            iron_mg=profile_data.iron_mg,
            magnesium_mg=profile_data.magnesium_mg,
            phosphorus_mg=profile_data.phosphorus_mg,
            potassium_mg=profile_data.potassium_mg,
            zinc_mg=profile_data.zinc_mg,
            copper_mg=profile_data.copper_mg,
            manganese_mg=profile_data.manganese_mg,
            selenium_mcg=profile_data.selenium_mcg,
            iodine_mcg=profile_data.iodine_mcg,
            fluoride_mg=profile_data.fluoride_mg,
            # Trace minerals
            chromium_mcg=profile_data.chromium_mcg,
            molybdenum_mcg=profile_data.molybdenum_mcg,
            boron_mg=profile_data.boron_mg,
            silicon_mg=profile_data.silicon_mg,
            vanadium_mcg=profile_data.vanadium_mcg,
            # Fatty acids
            omega_3_grams=profile_data.omega_3_grams,
            omega_6_grams=profile_data.omega_6_grams,
            omega_9_grams=profile_data.omega_9_grams,
            dha_grams=profile_data.dha_grams,
            epa_grams=profile_data.epa_grams,
            ala_grams=profile_data.ala_grams,
            la_grams=profile_data.la_grams,
            # Amino acids
            histidine_grams=profile_data.histidine_grams,
            isoleucine_grams=profile_data.isoleucine_grams,
            leucine_grams=profile_data.leucine_grams,
            lysine_grams=profile_data.lysine_grams,
            methionine_grams=profile_data.methionine_grams,
            phenylalanine_grams=profile_data.phenylalanine_grams,
            threonine_grams=profile_data.threonine_grams,
            tryptophan_grams=profile_data.tryptophan_grams,
            valine_grams=profile_data.valine_grams,
            # Phytochemicals
            beta_carotene_mcg=profile_data.beta_carotene_mcg,
            lycopene_mcg=profile_data.lycopene_mcg,
            lutein_mcg=profile_data.lutein_mcg,
            zeaxanthin_mcg=profile_data.zeaxanthin_mcg,
            anthocyanins_mg=profile_data.anthocyanins_mg,
            flavonoids_mg=profile_data.flavonoids_mg,
            polyphenols_mg=profile_data.polyphenols_mg,
            resveratrol_mg=profile_data.resveratrol_mg,
            quercetin_mg=profile_data.quercetin_mg,
            catechins_mg=profile_data.catechins_mg,
            # Other bioactive compounds
            caffeine_mg=profile_data.caffeine_mg,
            theobromine_mg=profile_data.theobromine_mg,
            theophylline_mg=profile_data.theophylline_mg,
            capsaicin_mg=profile_data.capsaicin_mg,
            curcumin_mg=profile_data.curcumin_mg,
            gingerol_mg=profile_data.gingerol_mg,
            allicin_mg=profile_data.allicin_mg,
            # Water and hydration
            water_ml=profile_data.water_ml,
            alcohol_grams=profile_data.alcohol_grams
        )
        
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_nutritional_profile(self, profile_id: int) -> Optional[NutritionalProfile]:
        """Get a nutritional profile by ID"""
        return self.db.query(NutritionalProfile).filter(NutritionalProfile.id == profile_id).first()

    def get_user_profiles(self, user_id: str, search_params: NutritionalProfileSearch) -> List[NutritionalProfile]:
        """Get nutritional profiles for a user with search parameters"""
        query = self.db.query(NutritionalProfile).filter(NutritionalProfile.user_id == user_id)
        
        if search_params.profile_name:
            query = query.filter(NutritionalProfile.profile_name.ilike(f"%{search_params.profile_name}%"))
        
        if search_params.is_default is not None:
            query = query.filter(NutritionalProfile.is_default == search_params.is_default)
        
        return query.offset(search_params.offset).limit(search_params.limit).all()

    def update_nutritional_profile(self, profile_id: int, profile_data: NutritionalProfileUpdate) -> Optional[NutritionalProfile]:
        """Update a nutritional profile"""
        profile = self.get_nutritional_profile(profile_id)
        if not profile:
            return None
        
        # If setting as default, unset other default profiles
        if profile_data.is_default:
            self.db.query(NutritionalProfile).filter(
                and_(
                    NutritionalProfile.user_id == profile.user_id,
                    NutritionalProfile.id != profile_id,
                    NutritionalProfile.is_default == True
                )
            ).update({"is_default": False})
        
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete_nutritional_profile(self, profile_id: int) -> bool:
        """Delete a nutritional profile"""
        profile = self.get_nutritional_profile(profile_id)
        if not profile:
            return False
        
        self.db.delete(profile)
        self.db.commit()
        return True

    # Daily Nutritional Intake Methods
    def create_daily_intake(self, user_id: str, intake_data: DailyNutritionalIntakeCreate) -> DailyNutritionalIntake:
        """Create or update daily nutritional intake"""
        # Check if intake already exists for this date
        existing_intake = self.db.query(DailyNutritionalIntake).filter(
            and_(
                DailyNutritionalIntake.user_id == user_id,
                DailyNutritionalIntake.intake_date == intake_data.intake_date
            )
        ).first()
        
        if existing_intake:
            # Update existing intake
            update_data = intake_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing_intake, field, value)
            
            # Recalculate percentages and scores
            self._calculate_intake_metrics(existing_intake)
            
            self.db.commit()
            self.db.refresh(existing_intake)
            return existing_intake
        else:
            # Create new intake
            intake = DailyNutritionalIntake(
                user_id=user_id,
                intake_date=intake_data.intake_date,
                profile_id=intake_data.profile_id,
                calories_consumed=intake_data.calories_consumed,
                protein_grams=intake_data.protein_grams,
                carbs_grams=intake_data.carbs_grams,
                fat_grams=intake_data.fat_grams,
                fiber_grams=intake_data.fiber_grams,
                sugar_grams=intake_data.sugar_grams,
                sodium_mg=intake_data.sodium_mg,
                # Advanced macronutrients
                saturated_fat_grams=intake_data.saturated_fat_grams,
                monounsaturated_fat_grams=intake_data.monounsaturated_fat_grams,
                polyunsaturated_fat_grams=intake_data.polyunsaturated_fat_grams,
                trans_fat_grams=intake_data.trans_fat_grams,
                cholesterol_mg=intake_data.cholesterol_mg,
                # Carbohydrate breakdown
                total_carbs_grams=intake_data.total_carbs_grams,
                net_carbs_grams=intake_data.net_carbs_grams,
                simple_carbs_grams=intake_data.simple_carbs_grams,
                complex_carbs_grams=intake_data.complex_carbs_grams,
                starch_grams=intake_data.starch_grams,
                # Micronutrients
                vitamin_a_mcg=intake_data.vitamin_a_mcg,
                vitamin_c_mg=intake_data.vitamin_c_mg,
                vitamin_d_mcg=intake_data.vitamin_d_mcg,
                vitamin_e_mg=intake_data.vitamin_e_mg,
                vitamin_k_mcg=intake_data.vitamin_k_mcg,
                thiamine_mg=intake_data.thiamine_mg,
                riboflavin_mg=intake_data.riboflavin_mg,
                niacin_mg=intake_data.niacin_mg,
                pantothenic_acid_mg=intake_data.pantothenic_acid_mg,
                pyridoxine_mg=intake_data.pyridoxine_mg,
                biotin_mcg=intake_data.biotin_mcg,
                folate_mcg=intake_data.folate_mcg,
                cobalamin_mcg=intake_data.cobalamin_mcg,
                # Minerals
                calcium_mg=intake_data.calcium_mg,
                iron_mg=intake_data.iron_mg,
                magnesium_mg=intake_data.magnesium_mg,
                phosphorus_mg=intake_data.phosphorus_mg,
                potassium_mg=intake_data.potassium_mg,
                zinc_mg=intake_data.zinc_mg,
                copper_mg=intake_data.copper_mg,
                manganese_mg=intake_data.manganese_mg,
                selenium_mcg=intake_data.selenium_mcg,
                iodine_mcg=intake_data.iodine_mcg,
                fluoride_mg=intake_data.fluoride_mg,
                # Trace minerals
                chromium_mcg=intake_data.chromium_mcg,
                molybdenum_mcg=intake_data.molybdenum_mcg,
                boron_mg=intake_data.boron_mg,
                silicon_mg=intake_data.silicon_mg,
                vanadium_mcg=intake_data.vanadium_mcg,
                # Fatty acids
                omega_3_grams=intake_data.omega_3_grams,
                omega_6_grams=intake_data.omega_6_grams,
                omega_9_grams=intake_data.omega_9_grams,
                dha_grams=intake_data.dha_grams,
                epa_grams=intake_data.epa_grams,
                ala_grams=intake_data.ala_grams,
                la_grams=intake_data.la_grams,
                # Amino acids
                histidine_grams=intake_data.histidine_grams,
                isoleucine_grams=intake_data.isoleucine_grams,
                leucine_grams=intake_data.leucine_grams,
                lysine_grams=intake_data.lysine_grams,
                methionine_grams=intake_data.methionine_grams,
                phenylalanine_grams=intake_data.phenylalanine_grams,
                threonine_grams=intake_data.threonine_grams,
                tryptophan_grams=intake_data.tryptophan_grams,
                valine_grams=intake_data.valine_grams,
                # Phytochemicals
                beta_carotene_mcg=intake_data.beta_carotene_mcg,
                lycopene_mcg=intake_data.lycopene_mcg,
                lutein_mcg=intake_data.lutein_mcg,
                zeaxanthin_mcg=intake_data.zeaxanthin_mcg,
                anthocyanins_mg=intake_data.anthocyanins_mg,
                flavonoids_mg=intake_data.flavonoids_mg,
                polyphenols_mg=intake_data.polyphenols_mg,
                resveratrol_mg=intake_data.resveratrol_mg,
                quercetin_mg=intake_data.quercetin_mg,
                catechins_mg=intake_data.catechins_mg,
                # Other bioactive compounds
                caffeine_mg=intake_data.caffeine_mg,
                theobromine_mg=intake_data.theobromine_mg,
                theophylline_mg=intake_data.theophylline_mg,
                capsaicin_mg=intake_data.capsaicin_mg,
                curcumin_mg=intake_data.curcumin_mg,
                gingerol_mg=intake_data.gingerol_mg,
                allicin_mg=intake_data.allicin_mg,
                # Water and hydration
                water_ml=intake_data.water_ml,
                alcohol_grams=intake_data.alcohol_grams
            )
            
            # Calculate percentages and scores
            self._calculate_intake_metrics(intake)
            
            self.db.add(intake)
            self.db.commit()
            self.db.refresh(intake)
            return intake

    def _calculate_intake_metrics(self, intake: DailyNutritionalIntake) -> None:
        """Calculate derived metrics for daily intake"""
        if intake.calories_consumed > 0:
            # Calculate macronutrient percentages
            intake.protein_percentage = (intake.protein_grams * 4) / intake.calories_consumed * 100
            intake.carbs_percentage = (intake.carbs_grams * 4) / intake.calories_consumed * 100
            intake.fat_percentage = (intake.fat_grams * 9) / intake.calories_consumed * 100
            
            # Calculate fiber density (grams per 1000 calories)
            intake.fiber_density = (intake.fiber_grams / intake.calories_consumed) * 1000
            
            # Calculate nutrient density score (simplified)
            micronutrient_score = 0
            micronutrient_count = 0
            
            # Check key micronutrients
            micronutrients = [
                intake.vitamin_a_mcg, intake.vitamin_c_mg, intake.vitamin_d_mcg,
                intake.vitamin_e_mg, intake.vitamin_k_mcg, intake.calcium_mg,
                intake.iron_mg, intake.magnesium_mg, intake.potassium_mg,
                intake.zinc_mg, intake.selenium_mcg
            ]
            
            for nutrient in micronutrients:
                if nutrient and nutrient > 0:
                    micronutrient_count += 1
                    micronutrient_score += min(nutrient / 100, 1)  # Normalize to 0-1
            
            if micronutrient_count > 0:
                intake.nutrient_density_score = (micronutrient_score / micronutrient_count) * 100
            else:
                intake.nutrient_density_score = 0

    def get_daily_intake(self, user_id: str, intake_date: date) -> Optional[DailyNutritionalIntake]:
        """Get daily intake for a specific date"""
        return self.db.query(DailyNutritionalIntake).filter(
            and_(
                DailyNutritionalIntake.user_id == user_id,
                DailyNutritionalIntake.intake_date == intake_date
            )
        ).first()

    def get_intake_range(self, user_id: str, start_date: date, end_date: date) -> List[DailyNutritionalIntake]:
        """Get daily intakes for a date range"""
        return self.db.query(DailyNutritionalIntake).filter(
            and_(
                DailyNutritionalIntake.user_id == user_id,
                DailyNutritionalIntake.intake_date >= start_date,
                DailyNutritionalIntake.intake_date <= end_date
            )
        ).order_by(DailyNutritionalIntake.intake_date).all()

    def calculate_average_intake(self, user_id: str, start_date: date, intakes: List[DailyNutritionalIntake]) -> Optional[DailyNutritionalIntake]:
        """Calculate average intake over a period"""
        if not intakes:
            return None
        
        # Calculate averages for all numeric fields
        avg_intake = DailyNutritionalIntake(
            user_id=user_id,
            intake_date=start_date,  # Use start date as reference
            calories_consumed=statistics.mean([i.calories_consumed for i in intakes]),
            protein_grams=statistics.mean([i.protein_grams for i in intakes]),
            carbs_grams=statistics.mean([i.carbs_grams for i in intakes]),
            fat_grams=statistics.mean([i.fat_grams for i in intakes]),
            fiber_grams=statistics.mean([i.fiber_grams for i in intakes]),
            sugar_grams=statistics.mean([i.sugar_grams for i in intakes]),
            sodium_mg=statistics.mean([i.sodium_mg for i in intakes]),
            # Calculate averages for other fields...
            # This would be a very long implementation for all fields
        )
        
        # Calculate derived metrics
        self._calculate_intake_metrics(avg_intake)
        
        return avg_intake

    # Food Composition Methods
    def create_food_composition(self, food_data: FoodCompositionCreate) -> FoodComposition:
        """Create a new food composition entry"""
        food = FoodComposition(
            food_name=food_data.food_name,
            scientific_name=food_data.scientific_name,
            food_group=food_data.food_group,
            sub_group=food_data.sub_group,
            calories=food_data.calories,
            protein_grams=food_data.protein_grams,
            carbs_grams=food_data.carbs_grams,
            fat_grams=food_data.fat_grams,
            fiber_grams=food_data.fiber_grams,
            sugar_grams=food_data.sugar_grams,
            sodium_mg=food_data.sodium_mg,
            # Advanced macronutrients
            saturated_fat_grams=food_data.saturated_fat_grams,
            monounsaturated_fat_grams=food_data.monounsaturated_fat_grams,
            polyunsaturated_fat_grams=food_data.polyunsaturated_fat_grams,
            trans_fat_grams=food_data.trans_fat_grams,
            cholesterol_mg=food_data.cholesterol_mg,
            # Food characteristics
            glycemic_index=food_data.glycemic_index,
            glycemic_load=food_data.glycemic_load,
            glycemic_index_level=food_data.glycemic_index_level,
            nutrient_density_score=food_data.nutrient_density_score,
            nutrient_density_level=food_data.nutrient_density_level,
            processing_level=food_data.processing_level,
            # Food safety and quality
            is_organic=food_data.is_organic,
            is_gmo_free=food_data.is_gmo_free,
            is_gluten_free=food_data.is_gluten_free,
            is_dairy_free=food_data.is_dairy_free,
            is_nut_free=food_data.is_nut_free,
            is_soy_free=food_data.is_soy_free,
            # Allergen information
            allergens=json.dumps(food_data.allergens) if food_data.allergens else None,
            cross_contamination_risks=json.dumps(food_data.cross_contamination_risks) if food_data.cross_contamination_risks else None,
            # Storage and preparation
            shelf_life_days=food_data.shelf_life_days,
            storage_conditions=json.dumps(food_data.storage_conditions) if food_data.storage_conditions else None,
            preparation_methods=json.dumps(food_data.preparation_methods) if food_data.preparation_methods else None,
            # Source and verification
            data_source=food_data.data_source,
            verification_status=food_data.verification_status
        )
        
        self.db.add(food)
        self.db.commit()
        self.db.refresh(food)
        return food

    def search_food_composition(self, search_params: FoodCompositionSearch) -> List[FoodComposition]:
        """Search food composition database"""
        query = self.db.query(FoodComposition)
        
        if search_params.food_name:
            query = query.filter(FoodComposition.food_name.ilike(f"%{search_params.food_name}%"))
        
        if search_params.food_group:
            query = query.filter(FoodComposition.food_group == search_params.food_group)
        
        if search_params.sub_group:
            query = query.filter(FoodComposition.sub_group == search_params.sub_group)
        
        if search_params.nutrient_density_level:
            query = query.filter(FoodComposition.nutrient_density_level == search_params.nutrient_density_level)
        
        if search_params.processing_level:
            query = query.filter(FoodComposition.processing_level == search_params.processing_level)
        
        if search_params.is_organic is not None:
            query = query.filter(FoodComposition.is_organic == search_params.is_organic)
        
        if search_params.is_gluten_free is not None:
            query = query.filter(FoodComposition.is_gluten_free == search_params.is_gluten_free)
        
        if search_params.is_dairy_free is not None:
            query = query.filter(FoodComposition.is_dairy_free == search_params.is_dairy_free)
        
        if search_params.allergens:
            for allergen in search_params.allergens:
                query = query.filter(FoodComposition.allergens.ilike(f"%{allergen}%"))
        
        return query.offset(search_params.offset).limit(search_params.limit).all()

    # Nutritional Analysis Methods
    def create_nutritional_analysis(self, user_id: str, analysis_data: NutritionalAnalysisCreate) -> NutritionalAnalysis:
        """Create a new nutritional analysis"""
        analysis = NutritionalAnalysis(
            user_id=user_id,
            analysis_date=analysis_data.analysis_date,
            analysis_type=analysis_data.analysis_type,
            total_calories=analysis_data.total_calories,
            calories_from_protein=analysis_data.calories_from_protein,
            calories_from_carbs=analysis_data.calories_from_carbs,
            calories_from_fat=analysis_data.calories_from_fat,
            calories_from_alcohol=analysis_data.calories_from_alcohol,
            protein_percentage=analysis_data.protein_percentage,
            carbs_percentage=analysis_data.carbs_percentage,
            fat_percentage=analysis_data.fat_percentage,
            alcohol_percentage=analysis_data.alcohol_percentage,
            nutrient_density_score=analysis_data.nutrient_density_score,
            fiber_density_score=analysis_data.fiber_density_score,
            protein_quality_score=analysis_data.protein_quality_score,
            micronutrient_adequacy_score=analysis_data.micronutrient_adequacy_score,
            overall_nutrition_score=analysis_data.overall_nutrition_score,
            nutrient_deficiencies=json.dumps(analysis_data.nutrient_deficiencies) if analysis_data.nutrient_deficiencies else None,
            excess_nutrients=json.dumps(analysis_data.excess_nutrients) if analysis_data.excess_nutrients else None,
            recommended_adjustments=json.dumps(analysis_data.recommended_adjustments) if analysis_data.recommended_adjustments else None,
            cardiovascular_health_score=analysis_data.cardiovascular_health_score,
            metabolic_health_score=analysis_data.metabolic_health_score,
            immune_support_score=analysis_data.immune_support_score,
            cognitive_health_score=analysis_data.cognitive_health_score,
            bone_health_score=analysis_data.bone_health_score,
            calorie_trend=analysis_data.calorie_trend,
            protein_trend=analysis_data.protein_trend,
            micronutrient_trend=analysis_data.micronutrient_trend,
            overall_trend=analysis_data.overall_trend,
            ai_insights=json.dumps(analysis_data.ai_insights) if analysis_data.ai_insights else None,
            personalized_recommendations=json.dumps(analysis_data.personalized_recommendations) if analysis_data.personalized_recommendations else None,
            risk_factors=json.dumps(analysis_data.risk_factors) if analysis_data.risk_factors else None,
            improvement_areas=json.dumps(analysis_data.improvement_areas) if analysis_data.improvement_areas else None
        )
        
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def get_nutritional_analyses(self, user_id: str, search_params: NutritionalAnalysisSearch) -> List[NutritionalAnalysis]:
        """Get nutritional analyses for a user"""
        query = self.db.query(NutritionalAnalysis).filter(NutritionalAnalysis.user_id == user_id)
        
        if search_params.analysis_type:
            query = query.filter(NutritionalAnalysis.analysis_type == search_params.analysis_type)
        
        if search_params.start_date:
            query = query.filter(NutritionalAnalysis.analysis_date >= search_params.start_date)
        
        if search_params.end_date:
            query = query.filter(NutritionalAnalysis.analysis_date <= search_params.end_date)
        
        if search_params.min_nutrition_score is not None:
            query = query.filter(NutritionalAnalysis.overall_nutrition_score >= search_params.min_nutrition_score)
        
        if search_params.max_nutrition_score is not None:
            query = query.filter(NutritionalAnalysis.overall_nutrition_score <= search_params.max_nutrition_score)
        
        return query.order_by(desc(NutritionalAnalysis.analysis_date)).offset(search_params.offset).limit(search_params.limit).all()

    # Health Metrics Methods
    def create_health_metric(self, user_id: str, metric_data: HealthMetricsCreate) -> HealthMetrics:
        """Create a new health metric entry"""
        metric = HealthMetrics(
            user_id=user_id,
            measurement_date=metric_data.measurement_date,
            metric_type=metric_data.metric_type,
            metric_value=metric_data.metric_value,
            metric_unit=metric_data.metric_unit,
            measurement_method=metric_data.measurement_method,
            notes=metric_data.notes
        )
        
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        return metric

    def get_health_metrics(self, user_id: str, metric_type: Optional[str] = None, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[HealthMetrics]:
        """Get health metrics for a user"""
        query = self.db.query(HealthMetrics).filter(HealthMetrics.user_id == user_id)
        
        if metric_type:
            query = query.filter(HealthMetrics.metric_type == metric_type)
        
        if start_date:
            query = query.filter(HealthMetrics.measurement_date >= start_date)
        
        if end_date:
            query = query.filter(HealthMetrics.measurement_date <= end_date)
        
        return query.order_by(desc(HealthMetrics.measurement_date)).all()

    # Dashboard Methods
    def get_nutritional_dashboard(self, user_id: str) -> NutritionalDashboard:
        """Get comprehensive nutritional dashboard for a user"""
        # Get current profile
        current_profile = self.db.query(NutritionalProfile).filter(
            and_(
                NutritionalProfile.user_id == user_id,
                NutritionalProfile.is_default == True
            )
        ).first()
        
        # Get today's intake
        today = date.today()
        today_intake = self.get_daily_intake(user_id, today)
        
        # Get weekly average
        week_start = today - timedelta(days=6)
        weekly_intakes = self.get_intake_range(user_id, week_start, today)
        weekly_average = self.calculate_average_intake(user_id, week_start, weekly_intakes)
        
        # Get monthly average
        month_start = today - timedelta(days=29)
        monthly_intakes = self.get_intake_range(user_id, month_start, today)
        monthly_average = self.calculate_average_intake(user_id, month_start, monthly_intakes)
        
        # Get recent analyses
        recent_analyses = self.get_nutritional_analyses(
            user_id,
            NutritionalAnalysisSearch(limit=5)
        )
        
        # Get recent health metrics
        health_metrics = self.get_health_metrics(user_id, start_date=today - timedelta(days=30))
        
        # Get correlations
        correlations = self.db.query(NutritionalCorrelation).filter(
            NutritionalCorrelation.user_id == user_id
        ).order_by(desc(NutritionalCorrelation.correlation_date)).limit(10).all()
        
        # Generate recommendations and alerts
        recommendations = self._generate_recommendations(user_id, today_intake, current_profile)
        alerts = self._generate_alerts(user_id, today_intake, current_profile)
        
        return NutritionalDashboard(
            user_id=user_id,
            current_profile=current_profile,
            today_intake=today_intake,
            weekly_average=weekly_average,
            monthly_average=monthly_average,
            recent_analyses=recent_analyses,
            health_metrics=health_metrics,
            correlations=correlations,
            recommendations=recommendations,
            alerts=alerts
        )

    def _generate_recommendations(self, user_id: str, today_intake: Optional[DailyNutritionalIntake], current_profile: Optional[NutritionalProfile]) -> List[str]:
        """Generate personalized recommendations based on current intake and profile"""
        recommendations = []
        
        if not today_intake or not current_profile:
            return recommendations
        
        # Check macronutrient balance
        if today_intake.protein_percentage and today_intake.protein_percentage < 15:
            recommendations.append("Consider increasing protein intake to support muscle health")
        
        if today_intake.fat_percentage and today_intake.fat_percentage < 20:
            recommendations.append("Add healthy fats like nuts, avocado, or olive oil to your meals")
        
        if today_intake.fiber_density and today_intake.fiber_density < 14:
            recommendations.append("Increase fiber intake with more vegetables, fruits, and whole grains")
        
        # Check micronutrient adequacy
        if today_intake.vitamin_d_mcg and today_intake.vitamin_d_mcg < 20:
            recommendations.append("Consider vitamin D supplementation or more sun exposure")
        
        if today_intake.iron_mg and today_intake.iron_mg < 18:
            recommendations.append("Include iron-rich foods like lean meat, spinach, or legumes")
        
        # Check hydration
        if today_intake.water_ml and today_intake.water_ml < 2000:
            recommendations.append("Increase water intake for better hydration")
        
        return recommendations

    def _generate_alerts(self, user_id: str, today_intake: Optional[DailyNutritionalIntake], current_profile: Optional[NutritionalProfile]) -> List[str]:
        """Generate alerts based on nutritional intake"""
        alerts = []
        
        if not today_intake or not current_profile:
            return alerts
        
        # Check for excessive sodium
        if today_intake.sodium_mg and today_intake.sodium_mg > 2300:
            alerts.append("High sodium intake detected - consider reducing processed foods")
        
        # Check for excessive sugar
        if today_intake.sugar_grams and today_intake.sugar_grams > 50:
            alerts.append("High sugar intake detected - consider reducing sugary foods and drinks")
        
        # Check for low calorie intake
        if today_intake.calories_consumed < 1200:
            alerts.append("Very low calorie intake - ensure you're meeting basic nutritional needs")
        
        # Check for high alcohol consumption
        if today_intake.alcohol_grams and today_intake.alcohol_grams > 28:  # ~2 drinks
            alerts.append("High alcohol consumption - consider moderation")
        
        return alerts
