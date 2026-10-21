import unittest
from unittest.mock import patch

from main import TravelRequest, get_trips, plan_trip


class TripEndpointTests(unittest.TestCase):
    def test_plan_trip_saves_once_and_get_trips_does_not_save(self):
        request = TravelRequest(
            destination="Ooty",
            days=2,
            budget=5000,
            travelers=2,
            places=[],
            activities=["Tourist Places"],
        )
        generated_plan = {
            "destination": "Ooty",
            "days": 2,
            "budget": 5000,
            "travelers": 2,
            "places": ["Ooty Botanical Garden"],
            "activities": ["Walk through the botanical gardens"],
            "itinerary": [
                {
                    "day": 1,
                    "places": ["Ooty Botanical Garden"],
                    "activities": ["Walk through the botanical gardens"],
                }
            ],
            "recommendations": [],
            "budget_summary": {},
        }

        with (
            patch("main.generate_travel_plan", return_value=generated_plan),
            patch("main.save_trip", return_value=42) as save_trip_mock,
            patch("main.get_all_trips", return_value=[]) as get_trips_mock,
        ):
            response = plan_trip(
                request,
                user_id=7,
                idempotency_key="request-1",
            )
            self.assertEqual(response["trip_id"], 42)
            save_trip_mock.assert_called_once_with(
                generated_plan,
                7,
                "request-1",
            )

            self.assertEqual(get_trips(user_id=7), {"trips": []})
            get_trips_mock.assert_called_once_with(7)
            save_trip_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
