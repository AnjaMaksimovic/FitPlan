# FitPlan - Domain-Specific Language for Nutrition and Training Planning

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 1. Project Description

FitPlan is a domain-specific language (DSL) designed for intelligent weekly nutrition and training planning. The language is implemented using the textX library for grammar definition and parsing, while Jinja2 is used for output generation.

Instead of manually tracking calories in spreadsheets or using rigid meal planning apps, users can write a simple `.fitplan` script that describes their recipes, meal options, workouts, and goals. The system then automatically:

- **Fetches nutritional data** from a built-in database of 60+ ingredients or the OpenFoodFacts API - no need to manually enter calories, protein, carbs, or fat
- **Generates a weekly meal plan** by distributing meal options across 7 days with smart filters (e.g. no repeating the same protein source for lunch and dinner)
- **Calculates workout calories** automatically using MET (Metabolic Equivalent of Task) values based on workout type, duration, and intensity
- **Produces interactive outputs** - HTML pages, nutritional reports, shopping lists, and a progress tracker where users log meals and workouts in real-time

The target users are fitness enthusiasts, nutritionists, and anyone who wants to plan their diet and training in a structured, reproducible way without writing code or using complex tools.

## 2. Technologies

- **Python 3.12+** - primary implementation language
- **textX** - grammar definition and parsing
- **Jinja2** - template engine for output generation
- **OpenFoodFacts API** - automatic nutritional data lookup with local caching
- **pygls** - Language Server Protocol for VS Code support
- **TypeScript** - VS Code extension

## 3. Syntax Example

### Defining recipes (no manual nutritional values needed)

```
// No need to define ingredients - the system knows that
// ChickenBreast has 165 kcal, 31g protein per 100g

recipe ChickenWithBroccoli {
    serves 2
    time 30 min
    difficulty easy
    ingredients {
        ChickenBreast 300 g
        Broccoli 250 g
        OliveOil 15 ml
    }
    steps {
        step "Cut chicken into cubes" duration 5 min
        step "Fry chicken until golden" duration 10 min temperature 180 C
        step "Add broccoli and stir fry" duration 8 min temperature 160 C
    }
    tags [highProtein, lowCarb]
}

recipe SalmonWithQuinoa {
    serves 2
    time 40 min
    difficulty medium
    ingredients {
        Salmon 300 g
        Quinoa 150 g
        Spinach 100 g
    }
    steps {
        step "Cook quinoa" duration 15 min
        step "Bake salmon" duration 15 min temperature 200 C
        step "Serve together with spinach"
    }
    tags [highProtein, omega3]
}

recipe TofuStirFry {
    serves 2
    time 25 min
    difficulty medium
    ingredients {
        Tofu 300 g
        BellPepper 150 g
        BrownRice 200 g
    }
    steps {
        step "Cook rice" duration 20 min
        step "Fry tofu and peppers" duration 10 min temperature 180 C
    }
    tags [vegan, highFiber]
}
```

### Defining meal options (system distributes automatically)

```
options breakfast_options {
    OatmealBowl
    EggsWithAvocado
    GreekYogurtBowl
}

options lunch_options {
    ChickenWithBroccoli
    SalmonWithQuinoa
    TofuStirFry
}

options dinner_options {
    SalmonWithQuinoa
    TofuStirFry
    ChickenWithBroccoli
}
```

### Defining workouts (calories calculated automatically)

```
// No need to specify calories burned - the system calculates
// using MET values: weightlifting/high/60min = ~420 kcal

workout StrengthTraining {
    type weightlifting
    duration 60 min
    intensity high
    days [Monday, Wednesday, Friday]
}

workout CardioRun {
    type running
    duration 30 min
    intensity medium
    days [Tuesday, Thursday]
}

workout YogaSession {
    type yoga
    duration 45 min
    intensity low
    days [Saturday]
}
```

### Creating a plan (no manual day-by-day scheduling)

```
plan WeightLossPlan {
    goal weightLoss
    target_calories 1800 kcal
    target_macros {
        protein 40 %
        carbs 30 %
        fat 30 %
    }
    meals {
        breakfast from breakfast_options
        lunch from lunch_options
        dinner from dinner_options
    }
    filters {
        no_repeat_same_day
        max_per_week ChickenWithBroccoli 3
    }
}
```

The system automatically generates a 7-day plan, choosing different meals for each day while respecting the filters.

## 4. Language Concepts

The language supports five core concepts:

| Concept | Description | Key Feature |
|---|---|---|
| `ingredient` | Custom food item with nutritional values | **Optional** - 60+ built-in ingredients + API lookup |
| `recipe` | Preparation using ingredients with steps | References ingredients by name - system resolves nutritional data |
| `options` | Meal variations per meal type | System auto-distributes across 7 days |
| `workout` | Training session with day assignments | Calories auto-calculated via MET table |
| `plan` | Weekly plan with goals and filters | No manual day-by-day scheduling needed |

### Ingredient Resolution

When a recipe references an ingredient, the system resolves nutritional data in this order:
1. **Custom ingredients** defined in the `.fitplan` file (if any)
2. **Built-in database** — 60+ common ingredients with verified nutritional values
3. **OpenFoodFacts API** — automatic online lookup with local caching for future use

### Workout Calorie Calculation

Calories burned are calculated using the MET (Metabolic Equivalent of Task) formula:

```
Calories = MET × body_weight_kg × duration_hours
```

MET values are based on the Compendium of Physical Activities (Ainsworth et al.), the same source used by fitness apps like MyFitnessPal and Fitbit.

### Smart Filters

Filters control how meals are distributed across the week:

| Filter | Description |
|---|---|
| `no_repeat_same_day` | Don't use same protein source for lunch and dinner on the same day |
| `max_per_week RecipeName N` | Limit a recipe to N appearances per week |

## 5. Generators

| Generator | Description |
|---|---|
| HTML | Styled web page with recipe cards and auto-generated weekly plan |
| Nutrition Report | Daily calorie and macro comparison against targets with ✅⬇️⬆️ indicators |
| Shopping List | Aggregated ingredients for the week, grouped by category, with interactive checkboxes |
| Markdown | Weekly schedule with recipes, workouts, and summary statistics |
| Progress Tracker | Interactive HTML where users log meals, track workouts, add extra food, and get activity suggestions for calorie overages |

### Progress Tracker Features

The progress tracker generates an interactive HTML page where users can:
- Check off completed meals and workouts
- Add unplanned extra meals with calorie counts
- See a real-time daily calorie balance bar (green = on target, red = over)
- Get automatic activity suggestions when exceeding the target (e.g. "Over by 200 kcal - try 23 min moderate running to compensate")
- View weekly summary statistics (total meals logged, workouts completed, average daily calories)

## 6. Validations

| Validation | Type | Description |
|---|---|---|
| Macros sum to 100% | Error | `protein% + carbs% + fat%` must equal exactly 100 |
| Minimum calories | Error | `target_calories` must be at least 1000 kcal |
| Positive nutritional values | Error | Calories, protein, carbs, fat cannot be negative |
| Recipe has ingredients | Error | Each recipe must have at least one ingredient |
| Recipe has steps | Error | Each recipe must have at least one step |
| Ingredients exist | Error | All ingredients must exist in built-in DB, custom definitions, or API |
| Options not empty | Error | Each options block must contain at least one recipe |
| Workout has days | Error | Each workout must be assigned to at least one day |
| Plan has meals | Error | Each plan must have at least one meal assignment |
| Goal-calorie consistency | Warning | Warns if goal contradicts calorie target |

## 7. VS Code Support

The project includes a VS Code extension with syntax highlighting for `.fitplan` files, context-aware code completion via LSP server (e.g. offering defined ingredient names inside a recipe block), hover documentation for keywords, and real-time error diagnostics.

## Contributors

- Anja Maksimovic E2 77/2024
- Biljana Mijic E2 63/2024
- Marija Ilic E2 28/2024
- Ivana Ilijin E2 106/2024

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
