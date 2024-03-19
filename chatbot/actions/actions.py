import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import logging

class ActionGetNutritionData(Action):
    def name(self) -> Text:
        return "action_get_nutrition_data"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        # Get food item and quantity from the user's message
        food_item = next(tracker.get_latest_entity_values("food"), None)
        quantity = next(tracker.get_latest_entity_values("quantity"), None)

        # Default quantity to 1 if not provided
        if not quantity:
            quantity = "1"

        logging.info(food_item)

        # Make API call to Edamam API
        url = "https://api.edamam.com/api/nutrition-data"
        app_id = "69a1423e"
        app_key = "72cee44c49996c105c8bf14ab1c78349"
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "ingr": quantity + " " + food_item,
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            nutrition_info = data.get('totalNutrients', {})
            if nutrition_info:
                message = "The nutrition data for " + quantity + " " + food_item + " is:\n"
                for nutrient, details in nutrition_info.items():
                    message += "- " + details.get("label", "Unknown") + ": " + str(details.get("quantity", "Unknown")) + " " + details.get("unit", "") + "\n"
                dispatcher.utter_message(text=message)
            else:
                dispatcher.utter_message(text="Sorry, I couldn't retrieve the nutrition data for " + quantity + " " + food_item)
        except requests.exceptions.HTTPError as http_err:
            dispatcher.utter_message(text="Sorry, there was a problem fetching the nutrition data for " + quantity + " " + food_item + ". Please try again later.")
        except Exception as err:
            dispatcher.utter_message(text="Sorry, something went wrong.")
            print(err)
        
        return []
