#!/usr/bin/env python3
"""
Audit and optionally fix per-serving calories for database recipes.

- Recomputes total calories from ingredients using a lightweight nutrient table
  and simple unit normalization (g/ml assumed where not specified).
- Compares computed per-serving vs stored per_serving_calories.
- Flags suspicious rows and, with --apply, updates per_serving_calories.

Usage:
  python backend/scripts/audit_and_fix_recipe_nutrition.py --limit 500 --dry-run
  python backend/scripts/audit_and_fix_recipe_nutrition.py --apply
"""

from __future__ import annotations

import argparse
import math
import os
import re
import sys
from typing import Dict, Optional

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session

try:
    from database import SessionLocal
    from models.recipe import Recipe, RecipeIngredient, Ingredient
except Exception as e:
    raise SystemExit(f"Failed to import DB models. Run from project root. Error: {e}")


# kcal per 100g (approximate). Add common items as needed.
NUTRIENT_KCAL_PER_100G: Dict[str, float] = {
    # fats/oils
    "olive oil": 884, "vegetable oil": 884, "butter": 717, "margarine": 717,
    # dairy
    "milk": 60, "whole milk": 60, "yogurt": 59, "plain yogurt": 59, "greek yogurt": 97,
    "cheese": 402, "swiss": 393, "swiss cheese": 393, "parmesan": 431, "cheddar": 403,
    # proteins
    "egg": 155, "eggs": 155, "chicken": 239, "chicken breast": 165, "ham": 145,
    # staples
    "flour": 364, "wheat flour": 364, "bread": 265, "rye bread": 259, "pasta": 131,
    "rice": 130, "sugar": 387, "honey": 304,
    # produce
    "mushroom": 22, "mushrooms": 22, "tomato": 18, "tomatoes": 18, "onion": 40, "red onion": 40,
    "cucumber": 16, "carrot": 41, "garlic": 149, "pepper": 20,
    # condiments
    "mayonnaise": 680, "mustard": 66, "soy sauce": 53, "tahini": 595, "sesame oil": 884,
}


def normalize_name(name: str) -> str:
    name = (name or "").strip().lower()
    # remove descriptors
    name = re.sub(r"\([^)]*\)", "", name)
    name = re.sub(r"[,;-].*", "", name)
    name = re.sub(r"\b(chopped|sliced|diced|minced|fresh|finely|coarsely|ground|toasted|peeled|seeded|cooked|raw|large|small)\b", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def kcal_for_ingredient(name: str, quantity: float, unit: str) -> Optional[float]:
    key = normalize_name(name)
    # map to a known key
    for k in NUTRIENT_KCAL_PER_100G.keys():
        if k in key:
            kcal100 = NUTRIENT_KCAL_PER_100G[k]
            break
    else:
        return None

    # unit normalization
    unit = (unit or "").strip().lower()
    grams = None
    if unit in ("g", "gram", "grams"):
        grams = quantity
    elif unit in ("ml", "milliliter", "milliliters"):
        # assume density ~ water unless oil (use 0.91 for oils)
        if "oil" in key:
            grams = quantity * 0.91
        else:
            grams = quantity
    elif unit in ("tbsp", "tablespoon", "tablespoons"):
        # approx conversions
        if "oil" in key or "mayonnaise" in key:
            grams = 14 * quantity
        else:
            grams = 15 * quantity
    elif unit in ("tsp", "teaspoon", "teaspoons"):
        grams = 5 * quantity
    else:
        # fallback: assume value is already grams
        grams = quantity

    kcal = (kcal100 / 100.0) * float(grams)
    return kcal


def compute_total_kcal(recipe: Recipe) -> Optional[float]:
    total = 0.0
    have_any = False
    for ri in recipe.ingredients:
        try:
            name = ri.ingredient.name if isinstance(ri.ingredient, Ingredient) else (getattr(ri, "name", None) or "")
            qty = float(ri.quantity or 0)
            unit = (ri.unit or "").lower()
            kcal = kcal_for_ingredient(name, qty, unit)
            if kcal is not None:
                total += kcal
                have_any = True
        except Exception:
            continue
    return total if have_any else None


def main():
    parser = argparse.ArgumentParser(description="Audit and fix per-serving calories for recipes")
    parser.add_argument("--limit", type=int, default=0, help="Max recipes to process (0 = all)")
    parser.add_argument("--apply", action="store_true", help="Apply fixes to database")
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes (default)")
    args = parser.parse_args()

    db: Session = SessionLocal()
    try:
        q = db.query(Recipe).order_by(Recipe.id.asc())
        if args.limit:
            q = q.limit(args.limit)
        recipes = q.all()

        fixed = 0
        flagged = 0
        scanned = 0
        for r in recipes:
            scanned += 1
            servings = float(r.servings or 1)
            stored_per_serving = float(r.per_serving_calories or 0)

            est_total = compute_total_kcal(r)
            if est_total is None or est_total <= 0:
                # Heuristic check for obviously wrong values
                if stored_per_serving <= 0 or stored_per_serving > 1500:
                    flagged += 1
                continue

            est_per_serving = est_total / max(1.0, servings)

            # Determine if suspicious or deviates significantly
            suspicious = (stored_per_serving <= 60) or (stored_per_serving >= 1200)
            deviation = abs(est_per_serving - stored_per_serving) / max(1.0, stored_per_serving)
            if suspicious or deviation >= 0.35:
                flagged += 1
                if args.apply and not args.dry_run:
                    r.per_serving_calories = int(round(est_per_serving))
                    db.add(r)
                    fixed += 1

        if args.apply and not args.dry_run:
            db.commit()

        print({
            "scanned": scanned,
            "flagged": flagged,
            "fixed": fixed,
            "applied": bool(args.apply and not args.dry_run),
        })

    finally:
        db.close()


if __name__ == "__main__":
    main()


