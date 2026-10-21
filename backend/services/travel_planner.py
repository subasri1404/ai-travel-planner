
# AI TRAVEL PLANNER - TRAVEL PLANNER SERVICE

DESTINATION_SUGGESTIONS = {
    "ooty": [
        {
            "place": "Ooty Botanical Garden",
            "activity": "Walk through the botanical gardens",
        },
        {
            "place": "Ooty Lake",
            "activity": "Explore the lakeside",
        },
        {
            "place": "Doddabetta Peak",
            "activity": "Take in the hilltop views",
        },
        {
            "place": "Ooty Rose Garden",
            "activity": "Walk through the rose garden",
        },
        {
            "place": "Ooty Tea Factory",
            "activity": "Learn about Nilgiri tea production",
        },
        {
            "place": "Pine Forest, Ooty",
            "activity": "Walk among the pine trees",
        },
    ],
}

GENERIC_INTERESTS = {
    "activities",
    "beaches",
    "food",
    "hotels",
    "museums",
    "nature",
    "parks",
    "restaurants",
    "resorts",
    "shopping",
    "temples",
    "tourist places",
}


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


def distribute_items(items, days):
    day_items = [[] for _ in range(days)]
    if not items:
        return day_items

    for index, item in enumerate(items):
        day_index = min(index * days // len(items), days - 1)
        day_items[day_index].append(item)

    return day_items


# 4. Create Day-by-Day Itinerary
def create_itinerary(trip):
    places_by_day = distribute_items(trip["places"], trip["days"])
    activities_by_day = distribute_items(trip["activities"], trip["days"])

    return [
        {
            "day": day,
            "places": places_by_day[day - 1],
            "activities": activities_by_day[day - 1],
        }
        for day in range(1, trip["days"] + 1)
    ]


# 5. Generate Recommendations
def generate_recommendations(destination, places, activities):
    recommendations = []

    if places:
        recommendations.append(
            f"Explore these places in {destination}: {', '.join(places)}."
        )
    else:
        recommendations.append(
            f"No curated place suggestions are available for {destination}. "
            "Add places you have researched to personalize each day."
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

    curated_suggestions = DESTINATION_SUGGESTIONS.get(
        trip["destination"].strip().casefold()
    )
    if curated_suggestions and not trip["places"]:
        trip["places"] = [suggestion["place"] for suggestion in curated_suggestions]
        custom_activities = [
            activity
            for activity in trip["activities"]
            if activity.strip().casefold() not in GENERIC_INTERESTS
        ]
        trip["activities"] = custom_activities or [
            suggestion["activity"] for suggestion in curated_suggestions
        ]
    else:
        trip["activities"] = [
            activity
            for activity in trip["activities"]
            if activity.strip().casefold() not in GENERIC_INTERESTS
        ]

    trip["itinerary"] = create_itinerary(trip)

    trip["recommendations"] = generate_recommendations(
        trip["destination"],
        trip["places"],
        trip["activities"]
    )
    if curated_suggestions and not places:
        trip["recommendations"].append(
            "These are curated suggestions, not live availability information. "
            "Check current opening hours and access before visiting."
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
