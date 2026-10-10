
# AI TRAVEL PLANNER - TRAVEL PLANNER SERVICE


# 1. Validate Trip Details
def validate_travel_plan(destination, days, budget, travelers):
    if not isinstance(destination, str) or not destination.strip():
        raise ValueError("Destination cannot be empty")

    if not isinstance(days, int) or isinstance(days, bool) or not 1 <= days <= 30:
        raise ValueError("Days must be between 1 and 30")

    if budget <= 0:
        raise ValueError("Budget must be greater than 0")

    if not isinstance(travelers, int) or isinstance(travelers, bool) or not 1 <= travelers <= 100:
        raise ValueError("Travelers must be between 1 and 100")

    return True


# 2. Create Trip
def create_trip(destination, days, budget, travelers, places=None, activities=None):
    validate_travel_plan(destination, days, budget, travelers)

    return {
        "destination": destination.strip(),
        "days": days,
        "budget": round(float(budget), 2),
        "travelers": travelers,
        "places": list(places or []),
        "activities": list(activities or [])
    }


# 3. Calculate Budget
def calculate_daily_budget(budget, days):
    return round(budget / days, 2)


def calculate_person_budget(budget, travelers):
    return round(budget / travelers, 2)


def calculate_daily_person_budget(budget, days, travelers):
    return round(budget / days / travelers, 2)


# 4. Create Day-by-Day Itinerary
def create_itinerary(trip):
    itinerary = []
    places = trip["places"]
    activities = trip["activities"]

    for day in range(1, trip["days"] + 1):
        day_plan = {
            "day": day,
            "places": [],
            "activities": []
        }

        if places:
            day_plan["places"] = [places[(day - 1) % len(places)]]

        if activities:
            day_plan["activities"] = [
                activities[(day - 1) % len(activities)]
            ]

        itinerary.append(day_plan)

    return itinerary


# 5. Generate Recommendations
def generate_recommendations(destination, places, activities):
    recommendations = []

    if places:
        recommendations.append(
            f"Explore these places in {destination}: {', '.join(places)}."
        )
    else:
        recommendations.append(
            f"Research popular tourist places in {destination}."
        )

    if activities:
        recommendations.append(
            "Suggested activities: " + ", ".join(activities) + "."
        )
    else:
        recommendations.append(
            "Choose activities based on your interests."
        )

    recommendations.append(
        "Keep some money aside for food, transport, and emergencies."
    )

    return recommendations


# 6. Generate Budget Summary
def generate_budget_summary(budget, days, travelers):
    return {
        "total_budget": round(budget, 2),
        "daily_budget": calculate_daily_budget(budget, days),
        "budget_per_person": calculate_person_budget(budget, travelers),
        "daily_budget_per_person": calculate_daily_person_budget(
            budget, days, travelers
        )
    }


# 7. Generate Complete Travel Plan
def generate_travel_plan(
    destination,
    days,
    budget,
    travelers,
    places=None,
    activities=None
):
    trip = create_trip(
        destination=destination,
        days=days,
        budget=budget,
        travelers=travelers,
        places=places,
        activities=activities
    )

    trip["itinerary"] = create_itinerary(trip)

    trip["recommendations"] = generate_recommendations(
        trip["destination"],
        trip["places"],
        trip["activities"]
    )

    trip["budget_summary"] = generate_budget_summary(
        trip["budget"],
        trip["days"],
        trip["travelers"]
    )

    trip["daily_budget"] = trip["budget_summary"]["daily_budget"]
    trip["person_budget"] = trip["budget_summary"]["budget_per_person"]
    trip["daily_person_budget"] = (
        trip["budget_summary"]["daily_budget_per_person"]
    )

    return trip
