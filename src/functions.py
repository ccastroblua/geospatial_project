import requests
import os
from dotenv import load_dotenv

from pymongo import MongoClient
conn = MongoClient("localhost:27017")
db = conn.get_database("ironhack")
c = db.get_collection("spain_companies")

load_dotenv()
gm_key = os.getenv("token")

# Function to send an specific request to Google Maps API:
def get_places(lat, lon, radius, keyword = "", type_ = ""):
    """
    Args:
    lat: Latitude
    lon: Longitude
    radius: Radius of the search near by
    keyword: To search for afinity
    type_: Different type of places to search ("restaurants", etc)
    """
    
    url_nearby_search = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    loc = str(lat) + "," + str(lon)
    
    parameters = {"key": gm_key, "location": loc, "radius": radius, "keyword": keyword, "type": type_}
    
    response = requests.get(
    url=url_nearby_search, 
    params = parameters
    )
    
    restaurants_data = response.json()
    
    return restaurants_data


# Function to create a list of dic for the weight matrix:
def weight_matrix(list_dic, initial_index, last_index):
    """
    ARGS:
    data = list of dicctionaries, json structured.
    initial_index = first index of the list to loop.
    last_index = last index of the list to loop.
    """
    new_list = list()

    for company in list_dic[initial_index: last_index]:
        n = company["name"]
        coord = {"type": "Point", "coordinates": [company["latitude"], company["longitude"]]}

        # First query for videogames companies near:
        query1 = {"$and": 
                 [{"location": 
                   {"$near": 
                    {"$geometry": coord, 
                    "$minDistance": 1, 
                    "$maxDistance": 1000
                  }}},
                   {"category_code": 
                    "games_video"},
                  {"name": 
                   {"$ne": n}}
                         ]}
        final_query1 = c.find(query1)
        n_results1 = len(list(final_query1))

        # Second query for companies with more than 1M dollares raised:
        query2 = {"$and": 
                 [{"location": 
                   {"$near": 
                    {"$geometry": coord, 
                    "$minDistance": 1, 
                    "$maxDistance": 1000
                  }}},
                   {"raised_amount": 
                    {"$gte": 1000000}},
                  {"name": 
                   {"$ne": n}}
                         ]}
        final_query2 = c.find(query2)
        n_results2 = len(list(final_query2))   

        # Now we create the rest weighting columns with Google Maps API:

        # Starbucks near:
        response1 = get_places(
            company["latitude"], 
            company["longitude"], 
            radius = 1000, 
            keyword = "starbucks"
        )

        api_results1 = len(response1["results"])

        # Airports near:
        response2 = get_places(
            company["latitude"], 
            company["longitude"], 
            radius = 1000, 
            type_ = "airport"
        )

        api_results2 = len(response2["results"])    

        # Basketball stadiums near:
        response3 = get_places(
            company["latitude"], 
            company["longitude"], 
            radius = 10000, 
            type_ = "stadium",
            keyword = "basketball"
        )

        api_results3 = len(response3["results"])   

        # Vegan restaurants near:
        response4 = get_places(
            company["latitude"], 
            company["longitude"], 
            radius = 1000, 
            type_ = "restaurant",
            keyword = "vegan"
        )

        api_results4 = len(response4["results"])   

        # Schools near:
        response5 = get_places(
            company["latitude"], 
            company["longitude"], 
            radius = 1000, 
            type_ = "school",
        )

        api_results5 = len(response5["results"])   

        # Party places near:
        response6 = get_places(
            company["latitude"], 
            company["longitude"], 
            radius = 1000, 
            type_ = "night_club",
        )

        api_results6 = len(response6["results"])   

        # dog hairdressers near:
        response7 = get_places(
            company["latitude"], 
            company["longitude"], 
            radius = 1000, 
            type_ = "pet_store",
            keyword = "hairdresser"
        )

        api_results7 = len(response7["results"])   

        # Let's create en new list
        new_list.append({
            "name": n,
            "latitude": company["latitude"],
            "longitude": company["longitude"],
            "location": coord, 
            "videogames_near": n_results1, 
            "1mcompanies_near": n_results2, 
            "starbucks_near": api_results1,
            "airports_near": api_results2,
            "basket_stad_near": api_results3,
            "vegans_near": api_results4,
            "schools_near": api_results5,
            "nightclubs_near": api_results6,
            "dog_hairdresser_near": api_results7,
        })

    return new_list

# This function add up the information of a query to a list in order to graphic that information with folium
def mongo_places(query_results, place_type, places_list):
    for i in query_results:
    
        name = i["name"]
        place_type = place_type
        latitude = i["latitude"]
        longitude = i["longitude"]

        dicc = {
            "name": name, 
            "place_type": place_type, 
            "latitude": latitude, 
            "longitude": longitude
        }

        places_list.append(dicc)


# This function add up the information of a Google Maps API request to a list in order to graphic that information with folium
def google_places(response, place_type, places_list):
    for result in response["results"]:
        name = result["name"]
        place_type = place_type
        latitude = result["geometry"]["location"]["lat"]
        longitude = result["geometry"]["location"]["lng"]

        dicc = {
            "name": name, 
            "place_type": place_type, 
            "latitude": latitude, 
            "longitude": longitude
        }

        places_list.append(dicc)