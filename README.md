# FitPlan — Domain-Specific Language for Nutrition and Training Planning

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 1. Project Description

FitPlan is a domain-specific language (DSL) designed for planning weekly nutrition and training programs. The language is implemented using the textX library for grammar definition and parsing, while Jinja2 is used for output generation.

Instead of manually tracking calories in spreadsheets or using rigid meal planning apps, users can write a simple `.fitplan` script that describes their ingredients, recipes, meals, and weekly plans. The system then automatically calculates nutritional values, compares daily intake against goals, and generates useful outputs — styled HTML pages, nutritional reports, shopping lists, and Markdown schedules.

The target users are fitness enthusiasts, nutritionists, and anyone who wants to plan their diet and training in a structured, reproducible way without writing code or using complex tools.

## 2. Technologies

- **Python 3.12+** — primary implementation language
- **textX** — grammar definition and parsing
- **Jinja2** — template engine for output generation
- **pygls** — Language Server Protocol for VS Code support
- **TypeScript** — VS Code extension

## 3. Syntax Example

### Basic example — defining an ingredient and a recipe

```
ingredient ChickenBreast {
    per 100g
    calories 165 kcal
    protein 31 g
    carbs 0 g
    fat 3.6 g
    category meat
}

ingredient Broccoli {
    per 100g
    calories 34 kcal
    protein 2.8 g
    carbs 6.6 g
    fat 0.4 g
    fiber 2.6 g
    category vegetable
}

recipe ChickenWithBroccoli {
    serves 2
    time 30 min
    difficulty easy
    ingredients {
        ChickenBreast 300 g
        Broccoli 250 g
    }
    steps {
        step "Cut chicken into cubes" duration 5 min
        step "Fry chicken until golden" duration 10 min temperature 180 C
        step "Add broccoli and stir fry" duration 8 min temperature 160 C
    }
    tags [highProtein, lowCarb]
}
```

### Full example — weekly weight loss plan

```
meal Lunch {
    ChickenWithBroccoli servings 1
}

meal Dinner {
    SalmonWithQuinoa servings 1
}

meal Breakfast {
    OatmealWithBanana servings 1
}

plan WeeklyWeightLoss {
    goal weightLoss
    target_calories 1800 kcal
    target_macros {
        protein 40 %
        carbs 30 %
        fat 30 %
    }
    day Monday {
        breakfast Breakfast
        lunch Lunch
        dinner Dinner
        workout running 45 min intensity medium burns 400 kcal
    }
    day Tuesday {
        breakfast Breakfast
        lunch Lunch
        dinner Dinner
        workout weightlifting 60 min intensity high burns 350 kcal
    }
    day Wednesday {
        breakfast Breakfast
        lunch Dinner
        dinner Lunch
        workout yoga 30 min intensity low burns 150 kcal
    }
}
```

## 4. Language Concepts

The language supports four core concepts that reference each other:

**`ingredient`** — defines a food item with nutritional values per 100g/100ml (calories, protein, carbs, fat, fiber), optional allergens and category (meat, fish, dairy, vegetable, fruit, grain, legume, fat, sweetener, other).

**`recipe`** — defines a recipe that references previously defined ingredients with amounts in various units (g, kg, ml, l, tbsp, tsp, piece). Includes step-by-step preparation instructions with optional duration and temperature.

**`meal`** — combines one or more recipes with specified serving counts into a single meal (breakfast, lunch, dinner, snack).

**`plan`** — defines a weekly nutrition and training plan. Contains a goal (weightLoss, muscleGain, maintenance, endurance), target daily calories, macronutrient distribution (must sum to 100%), and a day-by-day schedule of meals and workouts.

## 5. Generators

**HTML** — styled web page with recipe cards (nutritional summary, ingredients, preparation steps) and weekly plan overview with macronutrient charts.

**Nutrition Report** — detailed table comparing actual daily calorie and macronutrient intake against plan targets, with indicators showing whether each day is on target, below, or above.

**Shopping List** — aggregates all ingredients from the entire weekly plan, sums quantities of the same ingredient across different recipes and days, and groups them by category. Interactive HTML with checkboxes.

**Markdown** — weekly schedule in Markdown format with all recipes, daily meal tables, workout details, and weekly summary statistics.

## 6. Validations

- Macronutrient percentages (protein + carbs + fat) must sum to exactly 100%
- Target calorie intake must be at least 1000 kcal
- Nutritional values cannot be negative
- Each recipe must have at least one ingredient and one preparation step
- The same day cannot appear twice in a plan
- Warning if goal is inconsistent with target calories (e.g. weightLoss with very high calorie target)

## 7. VS Code Support

The project includes a VS Code extension with syntax highlighting for `.fitplan` files, context-aware code completion via LSP server (e.g. offering defined ingredient names inside a recipe block), hover documentation for keywords, and real-time error diagnostics.

## Contributors

- Anja Maksimovic E2 77/2024
- Biljana Mijic E2 63/2024
- Marija Ilic E2 28/2024
- Ivana Ilijin E2 106/2024

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
