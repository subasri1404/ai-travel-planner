import unittest

from services.travel_planner import generate_travel_plan


class TravelPlannerTests(unittest.TestCase):
    def test_ooty_itinerary_uses_curated_unique_place_suggestions(self):
        plan = generate_travel_plan(
            destination="Ooty",
            days=3,
            budget=10000,
            travelers=2,
            activities=["Tourist Places"],
        )

        places = [
            place
            for day in plan["itinerary"]
            for place in day["places"]
        ]
        activities = [
            activity
            for day in plan["itinerary"]
            for activity in day["activities"]
        ]

        self.assertEqual(len(plan["itinerary"]), 3)
        self.assertEqual(len(places), 6)
        self.assertEqual(len(places), len(set(places)))
        self.assertIn("Ooty Botanical Garden", places)
        self.assertIn("Doddabetta Peak", places)
        self.assertIn("Pine Forest, Ooty", places)
        self.assertEqual(len(activities), 6)
        self.assertNotIn("Tourist Places", activities)
        self.assertIn("budget_summary", plan)

    def test_unknown_destination_does_not_present_interest_as_an_activity(self):
        plan = generate_travel_plan(
            destination="An Unlisted Destination",
            days=2,
            budget=1000,
            travelers=1,
            activities=["Tourist Places"],
        )

        self.assertEqual(plan["itinerary"][0]["places"], [])
        self.assertTrue(
            all(not day["activities"] for day in plan["itinerary"])
        )
        self.assertTrue(
            any("No curated place suggestions" in item
                for item in plan["recommendations"])
        )

    def test_user_supplied_places_are_distributed_without_repeating(self):
        plan = generate_travel_plan(
            destination="Somewhere",
            days=2,
            budget=1000,
            travelers=1,
            places=["Museum A", "Park B", "Market C"],
            activities=["Museum visit"],
        )

        scheduled = [
            place
            for day in plan["itinerary"]
            for place in day["places"]
        ]
        self.assertCountEqual(scheduled, ["Museum A", "Park B", "Market C"])
        self.assertTrue(
            all("Tourist Places" not in day["activities"]
                for day in plan["itinerary"])
        )


if __name__ == "__main__":
    unittest.main()
