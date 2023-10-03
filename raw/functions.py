import hashlib
import json
import os

import requests

def get_data_from_api(api_url):
    try:
        response = requests.get(api_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def get_distictlist_from_json():
    # Parse the JSON data
    with open('./resources/units.json') as f:
        # load json
        data = json.load(f)

    # Extract the list of distinct "specialities" from the units
    specialities = set()
    for unit in data["units"]:
        specialities.update(unit["specialities"])

    # Convert the set of specialities to a list if needed
    specialities_list = list(specialities)

    # Print the list of distinct specialities
    print(specialities_list)


def calculate_md5_hash(binary_data):
    md5_hash = hashlib.md5()
    md5_hash.update(binary_data)
    md5_hex = md5_hash.hexdigest()
    return md5_hex