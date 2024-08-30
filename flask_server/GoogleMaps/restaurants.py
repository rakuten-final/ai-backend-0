import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

googleapi = os.getenv("GOOGLE_KEY_API")
geocodingapi = os.getenv("GEOCODING_KEY_API")

# print(googleapi)

def getRestaurants(latti, longi, keyword,radius=1000):
    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        "location": f"{latti},{longi}",
        "radius": radius,
        "type": "restaurant",
        "key": googleapi,
        "keyword": keyword
    }
    
    response = requests.get(url, params=params)
    
    with open("response.json", "w") as f:
        f.write(json.dumps(response.json(), indent=4))
    
    return response.json()