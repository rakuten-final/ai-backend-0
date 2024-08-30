from common_imports import *


def getCoordinates(location_name):
    googleapi = os.getenv("GOOGLE_KEY_API")
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location_name,
        "key": googleapi
    }
    
    response = requests.get(geocode_url, params=params)
    geocode_result = response.json()
    
    if geocode_result['status'] == 'OK':
        location = geocode_result['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        raise Exception("Could not get coordinates for the location.")

def getPlaces(location_name, place_type, keyword, radius=1000):
    googleapi = os.getenv("GOOGLE_KEY_API")
    latti, longi = getCoordinates(location_name)
    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        "location": f"{latti},{longi}",
        "radius": radius,
        "type": place_type,
        "key": googleapi,
        "keyword": keyword
    }
    
    response = requests.get(url, params=params)
    
    with open("response.json", "w") as f:
        f.write(json.dumps(response.json(), indent=4))
    
    return response.json()