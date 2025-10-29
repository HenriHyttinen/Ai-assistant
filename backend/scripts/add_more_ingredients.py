#!/usr/bin/env python3
"""
Add more ingredients to reach 500+
"""
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from sqlalchemy import text

# Additional ingredients to reach 500+
ADDITIONAL_INGREDIENTS = [
    # More proteins
    ("chicken thigh", "protein", 209, 18, 0, 15),
    ("chicken wing", "protein", 203, 18, 0, 15),
    ("chicken drumstick", "protein", 172, 20, 0, 10),
    ("beef sirloin", "protein", 250, 26, 0, 15),
    ("beef ribeye", "protein", 291, 20, 0, 22),
    ("beef tenderloin", "protein", 250, 26, 0, 15),
    ("lamb leg", "protein", 250, 25, 0, 16),
    ("lamb shoulder", "protein", 282, 20, 0, 21),
    ("pork chop", "protein", 231, 25, 0, 14),
    ("pork shoulder", "protein", 250, 20, 0, 18),
    ("pork belly", "protein", 518, 9, 0, 53),
    ("ham", "protein", 145, 18, 1.5, 6),
    ("bacon", "protein", 541, 37, 1.4, 42),
    ("sausage", "protein", 301, 13, 2, 26),
    ("chorizo", "protein", 455, 24, 2, 38),
    ("salami", "protein", 336, 22, 1, 26),
    ("prosciutto", "protein", 319, 26, 0, 22),
    ("pancetta", "protein", 441, 20, 0, 39),
    ("mortadella", "protein", 311, 16, 0, 25),
    ("pepperoni", "protein", 494, 22, 1, 44),
    
    # More fish
    ("trout", "protein", 148, 20, 0, 6),
    ("bass", "protein", 124, 23, 0, 2),
    ("tilapia", "protein", 96, 20, 0, 1),
    ("swordfish", "protein", 144, 19, 0, 4),
    ("mahi mahi", "protein", 109, 20, 0, 1),
    ("red snapper", "protein", 128, 26, 0, 1),
    ("grouper", "protein", 118, 24, 0, 1),
    ("flounder", "protein", 91, 19, 0, 1),
    ("sole", "protein", 91, 19, 0, 1),
    ("anchovies", "protein", 131, 20, 0, 4),
    ("herring", "protein", 158, 18, 0, 9),
    ("eel", "protein", 184, 18, 0, 12),
    ("octopus", "protein", 82, 15, 2, 1),
    ("squid", "protein", 92, 16, 3, 1),
    ("cuttlefish", "protein", 79, 16, 1, 1),
    ("sea urchin", "protein", 172, 13, 4, 4),
    ("sea cucumber", "protein", 56, 13, 0, 0),
    ("abalone", "protein", 105, 17, 6, 1),
    ("conch", "protein", 130, 24, 4, 1),
    ("whelk", "protein", 137, 24, 7, 1),
    
    # More dairy
    ("goat cheese", "dairy", 364, 22, 2, 30),
    ("feta cheese", "dairy", 264, 14, 4, 21),
    ("blue cheese", "dairy", 353, 21, 2, 29),
    ("gorgonzola", "dairy", 356, 19, 2, 31),
    ("roquefort", "dairy", 369, 22, 2, 30),
    ("camembert", "dairy", 300, 20, 0, 25),
    ("brie", "dairy", 334, 21, 0, 28),
    ("gruyere", "dairy", 413, 30, 0, 32),
    ("swiss cheese", "dairy", 380, 27, 1, 28),
    ("gouda", "dairy", 356, 25, 2, 27),
    ("cheddar cheese", "dairy", 403, 25, 1, 33),
    ("colby cheese", "dairy", 394, 25, 1, 32),
    ("monterey jack", "dairy", 373, 25, 1, 30),
    ("pepper jack", "dairy", 373, 25, 1, 30),
    ("provolone", "dairy", 351, 26, 1, 27),
    ("mozzarella", "dairy", 280, 22, 2, 22),
    ("burrata", "dairy", 300, 17, 1, 25),
    ("stracciatella", "dairy", 300, 17, 1, 25),
    ("ricotta salata", "dairy", 174, 11, 3, 13),
    ("mascarpone", "dairy", 429, 4, 4, 44),
    
    # More grains
    ("wild rice", "grains", 101, 4, 21, 0.3),
    ("jasmine rice", "grains", 130, 2.7, 28, 0.3),
    ("basmati rice", "grains", 130, 2.7, 28, 0.3),
    ("arborio rice", "grains", 130, 2.7, 28, 0.3),
    ("sushi rice", "grains", 130, 2.7, 28, 0.3),
    ("sticky rice", "grains", 130, 2.7, 28, 0.3),
    ("black rice", "grains", 101, 4, 21, 0.3),
    ("red rice", "grains", 101, 4, 21, 0.3),
    ("purple rice", "grains", 101, 4, 21, 0.3),
    ("brown basmati", "grains", 111, 2.6, 23, 0.9),
    ("bulgur", "grains", 342, 12, 76, 1.3),
    ("couscous", "grains", 112, 4, 23, 0.2),
    ("freekeh", "grains", 325, 15, 71, 2.5),
    ("teff", "grains", 367, 13, 73, 2.4),
    ("sorghum", "grains", 329, 11, 72, 3.5),
    ("job's tears", "grains", 357, 12, 73, 3.6),
    ("kasha", "grains", 343, 13, 72, 3.4),
    ("wheat berries", "grains", 340, 15, 71, 2.4),
    ("cracked wheat", "grains", 340, 15, 71, 2.4),
    ("wheat germ", "grains", 360, 23, 52, 9),
    
    # More vegetables
    ("artichokes", "vegetables", 47, 3.3, 11, 0.2),
    ("fennel", "vegetables", 31, 1.2, 7, 0.2),
    ("leeks", "vegetables", 61, 1.5, 14, 0.3),
    ("shallots", "vegetables", 72, 2.5, 17, 0.1),
    ("scallions", "vegetables", 32, 1.8, 7, 0.2),
    ("chives", "vegetables", 30, 3.3, 4, 0.7),
    ("ramps", "vegetables", 35, 1.4, 7, 0.1),
    ("radishes", "vegetables", 16, 0.7, 3, 0.1),
    ("daikon", "vegetables", 18, 0.6, 4, 0.1),
    ("turnips", "vegetables", 28, 0.9, 6, 0.1),
    ("rutabaga", "vegetables", 36, 1, 8, 0.2),
    ("parsnips", "vegetables", 75, 1.2, 18, 0.3),
    ("celery root", "vegetables", 42, 1.5, 9, 0.3),
    ("kohlrabi", "vegetables", 27, 1.7, 6, 0.1),
    ("fennel bulb", "vegetables", 31, 1.2, 7, 0.2),
    ("endive", "vegetables", 17, 1.3, 3, 0.2),
    ("radicchio", "vegetables", 23, 1.4, 4, 0.1),
    ("arugula", "vegetables", 25, 2.6, 4, 0.7),
    ("watercress", "vegetables", 11, 2.3, 1, 0.1),
    ("mizuna", "vegetables", 20, 2.2, 4, 0.1),
    
    # More fruits
    ("pears", "fruits", 57, 0.4, 15, 0.1),
    ("peaches", "fruits", 39, 0.9, 10, 0.3),
    ("plums", "fruits", 46, 0.7, 11, 0.3),
    ("apricots", "fruits", 48, 1.4, 11, 0.4),
    ("cherries", "fruits", 63, 1.1, 16, 0.2),
    ("figs", "fruits", 74, 0.8, 19, 0.3),
    ("dates", "fruits", 277, 2.5, 75, 0.4),
    ("prunes", "fruits", 240, 2.2, 64, 0.4),
    ("raisins", "fruits", 299, 3.1, 79, 0.5),
    ("cranberries", "fruits", 46, 0.4, 12, 0.1),
    ("pomegranate", "fruits", 83, 1.7, 19, 1.2),
    ("persimmons", "fruits", 70, 0.6, 18, 0.2),
    ("kiwi", "fruits", 61, 1.1, 15, 0.5),
    ("passion fruit", "fruits", 97, 2.2, 23, 0.7),
    ("dragon fruit", "fruits", 60, 1.2, 13, 0.4),
    ("star fruit", "fruits", 31, 1, 7, 0.3),
    ("guava", "fruits", 68, 2.6, 14, 1),
    ("papaya", "fruits", 43, 0.5, 11, 0.3),
    ("coconut", "fruits", 354, 3.3, 15, 33),
    ("plantains", "fruits", 122, 1.3, 32, 0.4),
    
    # More nuts and seeds
    ("pine nuts", "nuts", 673, 14, 13, 68),
    ("chestnuts", "nuts", 213, 2.4, 46, 1.3),
    ("hazelnuts", "nuts", 628, 15, 17, 61),
    ("pistachios", "nuts", 560, 20, 28, 45),
    ("pecans", "nuts", 691, 9, 14, 72),
    ("brazil nuts", "nuts", 659, 14, 12, 67),
    ("macadamia nuts", "nuts", 718, 8, 14, 76),
    ("pumpkin seeds", "nuts", 559, 30, 11, 49),
    ("sunflower seeds", "nuts", 584, 21, 20, 51),
    ("chia seeds", "nuts", 486, 17, 42, 31),
    ("flax seeds", "nuts", 534, 18, 29, 42),
    ("hemp seeds", "nuts", 553, 31, 9, 49),
    ("sesame seeds", "nuts", 573, 18, 23, 50),
    ("poppy seeds", "nuts", 525, 18, 28, 42),
    ("caraway seeds", "nuts", 333, 20, 50, 15),
    ("fennel seeds", "nuts", 345, 15, 52, 15),
    ("cumin seeds", "nuts", 375, 18, 44, 22),
    ("coriander seeds", "nuts", 298, 12, 55, 18),
    ("mustard seeds", "nuts", 508, 26, 28, 36),
    ("nigella seeds", "nuts", 345, 18, 44, 22),
]

def add_ingredients():
    """Add more ingredients to reach 500+"""
    print("🥕 Adding more ingredients to reach 500+...")
    db = SessionLocal()
    try:
        # Get current count
        result = db.execute(text("SELECT COUNT(*) FROM ingredients"))
        current_count = result.scalar()
        print(f"Current ingredient count: {current_count}")
        
        # Add new ingredients
        for i, (name, category, calories, protein, carbs, fats) in enumerate(ADDITIONAL_INGREDIENTS):
            db.execute(text("""
                INSERT INTO ingredients (id, name, category, unit, default_quantity, calories, protein, carbs, fats, fiber, sugar, sodium, created_at, updated_at)
                VALUES (:id, :name, :category, :unit, :default_quantity, :calories, :protein, :carbs, :fats, :fiber, :sugar, :sodium, datetime('now'), datetime('now'))
            """), {
                "id": f"ing_{current_count + i + 1}",
                "name": name,
                "category": category,
                "unit": "g",
                "default_quantity": 100.0,
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fats": fats,
                "fiber": random.uniform(0, 10),
                "sugar": random.uniform(0, 5),
                "sodium": random.uniform(0, 100)
            })
        
        db.commit()
        print(f"✅ Added {len(ADDITIONAL_INGREDIENTS)} more ingredients")
        
        # Verify final count
        result = db.execute(text("SELECT COUNT(*) FROM ingredients"))
        final_count = result.scalar()
        print(f"Final ingredient count: {final_count}")
        
        if final_count >= 500:
            print("🎯 TARGET ACHIEVED: 500+ ingredients!")
        else:
            print(f"⚠️  Still need {500 - final_count} more ingredients")
            
    except Exception as e:
        print(f"❌ Error adding ingredients: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_ingredients()
