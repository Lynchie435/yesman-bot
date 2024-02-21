import base64
import json
import os
import struct
import logging

logger = logging.getLogger(__name__)

def getbits(data, s, n):
    byte = s // 8
    val = struct.unpack('>I', data[byte:byte + 4])[0]
    val >>= (32 - (s & 7) - n)
    val &= (1 << n) - 1
    return val


def getvalue(code: str):
    st = str.encode(code)  # encode the code string to bytes
    data = base64.b64decode(st)  # base64 decode the bytes

    pos = 0  # set starting pos
    i = 0  # set loop counter
    while i < 3:  # loop 3 times
        length = getbits(data, pos, 5)
        val = getbits(data, pos + 5, length)

        if i == 2:
            return val  # returns the 3rd looped value

        pos += 5 + length
        i += 1  # increase loop counter

def getDivision(deckcode: str):
    try:

        # Read the JSON data from the file
        with open('./resources/divisions.json', 'r') as file:
            data_dict = json.load(file)

        # Merge "nato" and "pact" arrays into a single array
        combined_array = data_dict.get("nato", []) + data_dict.get("pact", [])

        # Function to retrieve an item by its 'id' from the combined array
        def get_item_by_id(arr, item_id):
            for item in arr:
                if item["id"] == item_id:
                    return item
            return None

        item_id_to_find = getvalue(deckcode)
        found_item = get_item_by_id(combined_array, item_id_to_find)

        if found_item:
            return found_item['name']
        else:
            return "Unknown"

    except Exception as e:
        logger.error(f"{e}")