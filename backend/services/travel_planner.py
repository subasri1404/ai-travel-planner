
# MAIN PROJECT CODE

def create_trip(destination, days, budget, travelers, places, activities):
    trip = {
        "destination": destination,
        "days": days,
        "budget": budget,
        "travelers": travelers,
        "places": places,
        "activities": activities
    }
    return trip

def calculate_daily_budget(budget, days):
    if days <= 0:
        return "Days must be greater than 0"
    return budget / days

# TEST CODE - REMOVE LATER (ALL TEST CODE REMOVE LATER)

trip = create_trip("Kodaikanal", 4, 15000, 4, ["Kodaikanal Lake", "Coaker's Walk", "Pillar Rocks"], 
                   ["Boating", "Walking", "Sightseeing"])

print(trip)

# TEST CODE - PLACES

print("Places:")

for place in trip["places"]:
    print("-", place)

# TEST CODE - ACTIVITIES

print("Activities:")

for activity in trip["activities"]:
    print("-", activity)

# TEST CODE - DAILY BUDGET

daily_budget = calculate_daily_budget(10000, 3)
print("Daily Budget:", daily_budget)

# TEST CODE - INVALID DAYS

print(calculate_daily_budget(10000, 0))