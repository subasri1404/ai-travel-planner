def create_trip(destination, days, budget):
    trip = {
        "destination": destination,
        "days": days,
        "budget": budget
    }
    return trip

def calculate_daily_budget(budget, days):
    if days <= 0:
        return "Days must be greater then 0"
    return budget / days

trip = create_trip("Ooty", 3, 10000)
print(trip)

daily_budget = calculate_daily_budget(10000, 3)
print("Daily Budget:", daily_budget)

print(calculate_daily_budget(10000, 0))