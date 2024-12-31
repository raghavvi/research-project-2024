import json
import math
from collections import defaultdict

from bson import ObjectId
from flask import Flask, request, render_template, redirect, url_for, jsonify
import time
from shapely.geometry import box
from pyproj import Transformer, Proj, transform
from geopy.exc import GeocoderTimedOut
import geopandas as gpd
from key import key
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import os
from models import db, CustomJSONEncoder, IntervalOne, IntervalTwo, \
    IntervalThree, IntervalFour, IntervalFive, IntervalSix, FilteredModel
from models import Model
import pandas as pd
import numpy as np

load_dotenv()

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

app.config['MONGODB_SETTINGS'] = {
    'db': 'sample_geospatial',
    'host': os.getenv('MONGODB_URI'),
}
db.init_app(app)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


class UserData:
    latitude = None
    longitude = None
    interval = None
    radius = 0
    units = None
    grid = None

    def __init__(self):
        self.safecoordinates = []
        self.workcoordinates = []
        self.currentcoordinates = []
        self.destinationcoordinates = []

    # Convert radius and units (meters) to distance.
    # Create geometry to see if points fall within the radius (safe,current,work)

    def add_safe_coordinates(self, latitude, longitude):
        self.safecoordinates.append(longitude)
        self.safecoordinates.append(latitude)

    def add_work_coordinates(self, latitude, longitude):
        self.workcoordinates.append(longitude)
        self.workcoordinates.append(latitude)

    def add_current_coordinates(self, latitude, longitude):
        self.currentcoordinates.append(longitude)
        self.currentcoordinates.append(latitude)

    def add_destination_coordinates(self, latitude, longitude):
        self.destinationcoordinates.append(longitude)
        self.destinationcoordinates.append(latitude)


def load_dataset():
    pipeline = [
        {
            '$addFields': {
                'point': {
                    'type': 'Point',
                    'coordinates': ['$LONGITUDE_X', '$LATITUDE_X']
                }
            }
        }
    ]

    result = Model.objects().aggregate(*pipeline)

    hourpipeline = [
        {
            '$addFields': {
                'hour': {
                    '$substr': ['$time', 0, 2]
                }
            }
        }
    ]

    hour_result = Model.objects().aggregate(*hourpipeline)
    hour_result_list = [doc for doc in hour_result]

    return hour_result_list


def get_difference_in_years():
    combined_pipeline = [
        {
            "$match": {
                "DATE_REPORTED": {
                    "$ne": "",  # Exclude empty strings
                    "$exists": True,  # Ensure the field exists
                    "$type": "string"  # Ensure it's a string
                }
            }
        },
        {
            "$addFields": {
                "year": {
                    "$substr": ["$DATE_REPORTED", 6, 4]
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "maxYear": {"$max": "$year"},
                "minYear": {"$min": "$year"}
            }
        }
    ]
    result = FilteredModel.objects().aggregate(*combined_pipeline)
    result = list(result)
    print("result0",result[0])
    if result:
        max_year = result[0]["maxYear"]
        min_year = result[0]["minYear"]
        print(f"Max Year: {max_year}, Min Year: {min_year}")
        max_year = int(max_year)
        min_year = int(min_year)
        difference = max_year - min_year
        return difference
    else:
        print("No data found")
        return 0


# filtered_records = Model.objects.filter(INCIDENT_NO__startswith="COPY OF")
# print(f"Filtered records count: {filtered_records.count()}")
# filtered_records.delete()
# print("Records starting with 'COPY OF' have been deleted.")
# print("Updated Model count", Model.objects.count())

# @app.route('/removeduplicates')
# def remove_duplicates():
#     try:
#         print("Initial IntervalTwo count:", IntervalTwo.objects.count())
#
#         # Group records by INCIDENT_NO
#         incident_count = defaultdict(list)
#         for record in IntervalTwo.objects():
#             incident_no = record.INCIDENT_NO
#             if incident_no:
#                 incident_count[incident_no].append(record)
#
#         # Identify duplicates
#         duplicates = {key: value for key, value in incident_count.items() if len(value) > 1}
#         print("Duplicate keys before cleanup:", duplicates.keys())
#
#         # Safeguard: Log the duplicates to be deleted
#         total_deletes = 0
#
#         # Process duplicates
#         for incident_no, records in duplicates.items():
#             # Keep the first record, delete the rest
#             for duplicate in records[1:]:
#                 print(f"Deleting record with ADDRESS_X: {duplicate.ADDRESS_X}, INCIDENT_NO: {incident_no}")
#                 duplicate.delete()
#                 total_deletes += 1
#
#         print(f"Total records deleted: {total_deletes}")
#         print("Updated IntervalTwo count:", IntervalTwo.objects.count())
#
#         return jsonify({"status": "success", "message": f"Duplicates removed. Total deleted: {total_deletes}"}), 200
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500


def load_dataset2():
    combined_pipeline = [
        {
            '$addFields': {
                'point': {
                    'type': 'Point',
                    'coordinates': ['$LONGITUDE_X', '$LATITUDE_X']
                }
            }
        },
        {
            '$addFields': {
                'time': {
                    '$substr': ['$DATE_REPORTED', 11, 13]
                }
            }
        },
        {
            "$addFields": {
                "ampm": {
                    "$substr": ["$DATE_REPORTED", 20, 2]
                }
            }
        },
        {
            '$addFields': {
                'hour': {
                    '$substr': ['$time', 0, 2]
                }
            }
        }
    ]

    hour_result = Model.objects(INCIDENT_NO__ne=None).aggregate(*combined_pipeline, batchSize=100)
    hour_result_list = [
        doc for doc in hour_result
        if doc.get('LONGITUDE_X') != 999999.0 and doc.get('LATITUDE_X') != 999999.0
    ]
    print("hour_result_list", hour_result_list[0:10])

    return hour_result_list


@app.route('/updateattributes')
def update_attributes():
    try:
        Model.objects(DATE_REPORTED=None).update(set__DATE_REPORTED="NA")
        Model.objects(DATE_FROM=None).update(set__DATE_FROM="NA")
        Model.objects(DATE_TO=None).update(set__DATE_TO="NA")
        Model.objects(OPENING=None).update(set__OPENING="NA")
        Model.objects(LOCATION=None).update(set__LOCATION="NA")
        Model.objects(THEFT_CODE=None).update(set__THEFT_CODE="NA")
        Model.objects(FLOOR=None).update(set__FLOOR="NA")
        Model.objects(WEAPONS=None).update(set__WEAPONS="NA")
        Model.objects(DATE_OF_CLEARANCE=None).update(set__DATE_OF_CLEARANCE="NA")
        Model.objects(ADDRESS_X=None).update(set__ADDRESS_X="NA")
        Model.objects(LONGITUDE_X=None).update(set__LONGITUDE_X=999999.0)
        Model.objects(LATITUDE_X=None).update(set__LATITUDE_X=999999.0)
        return jsonify({"status": "success", "message": 200})
    except Exception as e:
        # Handle exceptions if the update fails
        return jsonify({"status": "error", "message": str(e)}), 500


def filter_time_interval(interval, data):
    if interval == "12AM-3AM":
        newlist = [result for result in data if
                   (result.get('hour') in ['12', '01', '02', '03']) and result.get('ampm') == 'AM']
    elif interval == '4AM-7AM':
        newlist = [result for result in data if
                   (result.get('hour') in ['04', '05', '06', '07']) and result.get('ampm') == 'AM']
    elif interval == "8AM-11AM":
        newlist = [result for result in data if
                   (result.get('hour') in ['08', '09', '10', '11']) and result.get('ampm') == 'AM']
    elif interval == "12PM-3PM":
        newlist = [result for result in data if
                   (result.get('hour') in ['12', '01', '02', '03']) and result.get('ampm') == 'PM']
    elif interval == "4PM-7PM":
        newlist = [result for result in data if
                   (result.get('hour') in ['04', '05', '06', '07']) and result.get('ampm') == 'PM']
    elif interval == "8PM-11PM":
        newlist = [result for result in data if
                   (result.get('hour') in ['08', '09', '10', '11']) and result.get('ampm') == 'PM']
    else:
        newlist = [result for result in data]
        print("newlist0", newlist[0])
    return newlist


# add ampm
def filter_time_interval_old(interval, data):
    if interval == "12AM-3AM":
        newlist = [result for result in data if result.get('hour') == '00' or result.get('hour') == '01'
                   or result.get('hour') == '02' or result.get('hour') == '03']
    elif interval == '4AM-7AM':
        newlist = [result for result in data if result.get('hour') == '04' or result.get('hour') == '05'
                   or result.get('hour') == '06' or result.get('hour') == '07']
    elif interval == "8AM-11AM":
        newlist = [result for result in data if result.get('hour') == '08' or result.get('hour') == '09'
                   or result.get('hour') == '10' or result.get('hour') == '11']
    elif interval == "12PM-3PM":
        newlist = [result for result in data if result.get('hour') == '12' or result.get('hour') == '13'
                   or result.get('hour') == '14' or result.get('hour') == '15']
    elif interval == "4PM-7PM":
        newlist = [result for result in data if result.get('hour') == '16' or result.get('hour') == '17'
                   or result.get('hour') == '18' or result.get('hour') == '19']
    elif interval == "8PM-11PM":
        newlist = [result for result in data if result.get('hour') == '20' or result.get('hour') == '21'
                   or result.get('hour') == '22' or result.get('hour') == '23']
    else:
        newlist = [result for result in data if result.get('hour') == '00' or result.get('hour') == '01'
                   or result.get('hour') == '02' or result.get('hour') == '03' or result.get('hour') == '04'
                   or result.get('hour') == '05' or result.get('hour') == '06' or result.get('hour') == '07'
                   or result.get('hour') == '08' or result.get('hour') == '09' or result.get('hour') == '10'
                   or result.get('hour') == '11' or result.get('hour') == '12' or result.get('hour') == '13'
                   or result.get('hour') == '14' or result.get('hour') == '15' or result.get('hour') == '16'
                   or result.get('hour') == '17' or result.get('hour') == '18' or result.get('hour') == '19'
                   or result.get('hour') == '20' or result.get('hour') == '21' or result.get('hour') == '22'
                   or result.get('hour') == '23']
    return newlist


def filter_dataset(interval, data):
    # #Filter out crime incidents that do not have a location
    point_results = [result for result in data if result.get('point') != [999999.0, 999999.0]]
    print("point_results", point_results[0:5])

    heavy_crime_list = ['FELONIOUS ASSAULT', 'ASSAULT', 'AGGRAVATED BURGLARY',
                        'AGGRAVATED ROBBERY', 'RAPE', 'ROBBERY', 'MURDER']
    offense_result = [result for result in point_results if result.get('OFFENSE') in heavy_crime_list]
    print("offense_result", offense_result[0:5])
    filtered_results = filter_time_interval(interval, offense_result)

    return filtered_results


def switch_grids2(grid, interval):
    file_all_700meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '700metersAll.json')
    file_12am_3am_700meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '700meters12AM-3AM.json')
    file_4am_7am_700meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '700meters4AM-7AM.json')
    file_8am_11am_700meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '700meters8AM-11AM.json')
    file_12pm_3pm_700meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '700meters12PM-3PM.json')
    file_4pm_7pm_700meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '700meters4PM-7PM.json')
    file_8pm_11pm_700meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '700meters8PM-11PM.json')
    file_all_750meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '750metersAll.json')
    file_12am_3am_750meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '750meters12AM-3AM.json')
    file_4am_7am_750meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '750meters4AM-7AM.json')
    file_8am_11am_750meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '750meters8AM-11AM.json')
    file_12pm_3pm_750meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '750meters12PM-3PM.json')
    file_4pm_7pm_750meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '750meters4PM-7PM.json')
    file_8pm_11pm_750meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '750meters8PM-11PM.json')
    file_all_800meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '800metersAll.json')
    file_12am_3am_800meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '800meters12AM-3AM.json')
    file_4am_7am_800meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '800meters4AM-7AM.json')
    file_8am_11am_800meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '800meters8AM-11AM.json')
    file_12pm_3pm_800meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '800meters12PM-3PM.json')
    file_4pm_7pm_800meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '800meters4PM-7PM.json')
    file_8pm_11pm_800meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '800meters8PM-11PM.json')
    file_all_850meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '850metersAll.json')
    file_12am_3am_850meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '850meters12AM-3AM.json')
    file_4am_7am_850meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '850meters4AM-7AM.json')
    file_8am_11am_850meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '850meters8AM-11AM.json')
    file_12pm_3pm_850meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '850meters12PM-3PM.json')
    file_4pm_7pm_850meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '850meters4PM-7PM.json')
    file_8pm_11pm_850meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '850meters8PM-11PM.json')
    file_all_900meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '900metersAll.json')
    file_12am_3am_900meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '900meters12AM-3AM.json')
    file_4am_7am_900meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '900meters4AM-7AM.json')
    file_8am_11am_900meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '900meters8AM-11AM.json')
    file_12pm_3pm_900meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '900meters12PM-3PM.json')
    file_4pm_7pm_900meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '900meters4PM-7PM.json')
    file_8pm_11pm_900meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '900meters8PM-11PM.json')
    file_all_950meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '950metersAll.json')
    file_12am_3am_950meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '950meters12AM-3AM.json')
    file_4am_7am_950meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '950meters4AM-7AM.json')
    file_8am_11am_950meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '950meters8AM-11AM.json')
    file_12pm_3pm_950meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '950meters12PM-3PM.json')
    file_4pm_7pm_950meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '950meters4PM-7PM.json')
    file_8pm_11pm_950meters = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '950meters8PM-11PM.json')
    file_all_1kilometer = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '1kilometerAll.json')
    file_12am_3am_1kilometer = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '1kilometer12AM-3AM.json')
    file_4am_7am_1kilometer = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '1kilometer4AM-7AM.json')
    file_8am_11am_1kilometer = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '1kilometer8AM-11AM.json')
    file_12pm_3pm_1kilometer = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '1kilometer12PM-3PM.json')
    file_4pm_7pm_1kilometer = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '1kilometer4PM-7PM.json')
    file_8pm_11pm_1kilometer = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '1kilometer8PM-11PM.json')
    file_all_1mile = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '1mileAll.json')
    file_12am_3am_1mile = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '1mile12AM-3AM.json')
    file_4am_7am_1mile = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '1mile4AM-7AM.json')
    file_8am_11am_1mile = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '1mile8AM-11AM.json')
    file_12pm_3pm_1mile = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '1mile12PM-3PM.json')
    file_4pm_7pm_1mile = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '1mile4PM-7PM.json')
    file_8pm_11pm_1mile = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '1mile8PM-11PM.json')

    if grid == "700 meters" and interval == "12AM-11PM":
        try:
            with open(file_all_700meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "700 meters" and interval == "12AM-3AM":
        try:
            with open(file_12am_3am_700meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "700 meters" and interval == "4AM-7AM":
        try:
            with open(file_4am_7am_700meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "700 meters" and interval == "8AM-11AM":
        try:
            with open(file_8am_11am_700meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "700 meters" and interval == "12PM-3PM":
        try:
            with open(file_12pm_3pm_700meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "700 meters" and interval == "4PM-7PM":
        try:
            with open(file_4pm_7pm_700meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "700 meters" and interval == "8PM-11PM":
        try:
            with open(file_8pm_11pm_700meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "750 meters" and interval == "12AM-11PM":
        try:
            with open(file_all_750meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "750 meters" and interval == "12AM-3AM":
        try:
            with open(file_12am_3am_750meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "750 meters" and interval == "4AM-7AM":
        try:
            with open(file_4am_7am_750meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "750 meters" and interval == "8AM-11AM":
        try:
            with open(file_8am_11am_750meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "750 meters" and interval == "12PM-3PM":
        try:
            with open(file_12pm_3pm_750meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "750 meters" and interval == "4PM-7PM":
        try:
            with open(file_4pm_7pm_750meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "750 meters" and interval == "8PM-11PM":
        try:
            with open(file_8pm_11pm_750meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "800 meters" and interval == "12AM-11PM":
        try:
            with open(file_all_800meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "800 meters" and interval == "12AM-3AM":
        try:
            with open(file_12am_3am_800meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "800 meters" and interval == "4AM-7AM":
        try:
            with open(file_4am_7am_800meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "800 meters" and interval == "8AM-11AM":
        try:
            with open(file_8am_11am_800meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "800 meters" and interval == "12PM-3PM":
        try:
            with open(file_12pm_3pm_800meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "800 meters" and interval == "4PM-7PM":
        try:
            with open(file_4pm_7pm_800meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "800 meters" and interval == "8PM-11PM":
        try:
            with open(file_8pm_11pm_800meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "850 meters" and interval == "12AM-11PM":
        try:
            with open(file_all_850meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "850 meters" and interval == "12AM-3AM":
        try:
            with open(file_12am_3am_850meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "850 meters" and interval == "4AM-7AM":
        try:
            with open(file_4am_7am_850meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "850 meters" and interval == "8AM-11AM":
        try:
            with open(file_8am_11am_850meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "850 meters" and interval == "12PM-3PM":
        try:
            with open(file_12pm_3pm_850meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "850 meters" and interval == "4PM-7PM":
        try:
            with open(file_4pm_7pm_850meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "850 meters" and interval == "8PM-11PM":
        try:
            with open(file_8pm_11pm_850meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "900 meters" and interval == "12AM-11PM":
        try:
            with open(file_all_900meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "900 meters" and interval == "12AM-3AM":
        try:
            with open(file_12am_3am_900meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "900 meters" and interval == "4AM-7AM":
        try:
            with open(file_4am_7am_900meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "900 meters" and interval == "8AM-11AM":
        try:
            with open(file_8am_11am_900meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "900 meters" and interval == "12PM-3PM":
        try:
            with open(file_12pm_3pm_900meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "900 meters" and interval == "4PM-7PM":
        try:
            with open(file_4pm_7pm_900meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "900 meters" and interval == "8PM-11PM":
        try:
            with open(file_8pm_11pm_900meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "950 meters" and interval == "12AM-11PM":
        try:
            with open(file_all_950meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "950 meters" and interval == "12AM-3AM":
        try:
            with open(file_12am_3am_950meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "950 meters" and interval == "4AM-7AM":
        try:
            with open(file_4am_7am_950meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "950 meters" and interval == "8AM-11AM":
        try:
            with open(file_8am_11am_950meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "950 meters" and interval == "12PM-3PM":
        try:
            with open(file_12pm_3pm_950meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "950 meters" and interval == "4PM-7PM":
        try:
            with open(file_4pm_7pm_950meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "950 meters" and interval == "8PM-11PM":
        try:
            with open(file_8pm_11pm_950meters, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "1 kilometer" and interval == "12AM-11PM":
        try:
            with open(file_all_1kilometer, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "1 kilometer" and interval == "12AM-3AM":
        try:
            with open(file_12am_3am_1kilometer, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "1 kilometer" and interval == "4AM-7AM":
        try:
            with open(file_4am_7am_1kilometer, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "1 kilometer" and interval == "8AM-11AM":
        try:
            with open(file_8am_11am_1kilometer, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "1 kilometer" and interval == "12PM-3PM":
        try:
            with open(file_12pm_3pm_1kilometer, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "1 kilometer" and interval == "4PM-7PM":
        try:
            with open(file_4pm_7pm_1kilometer, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "1 kilometer" and interval == "8PM-11PM":
        try:
            with open(file_8pm_11pm_1kilometer, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "1 mile" and interval == "12AM-11PM":
        try:
            with open(file_all_1mile, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "1 mile" and interval == "12AM-3AM":
        try:
            with open(file_12am_3am_1mile, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "1 mile" and interval == "4AM-7AM":
        try:
            with open(file_4am_7am_1mile, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "1 mile" and interval == "8AM-11AM":
        try:
            with open(file_8am_11am_1mile, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "1 mile" and interval == "12PM-3PM":
        try:
            with open(file_12pm_3pm_1mile, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "1 mile" and interval == "4PM-7PM":
        try:
            with open(file_4pm_7pm_1mile, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None
    elif grid == "1 mile" and interval == "8PM-11PM":
        try:
            with open(file_8pm_11pm_1mile, 'r') as file:
                datajson = json.load(file)
            appended_list = datajson.get("appended_list", [])
            return appended_list
        except FileNotFoundError:
            print("No file found: ", grid, interval)
            return None


def coord_lister(geom):
    coords = list(geom.exterior.coords)
    return (coords)


def get_radius(radius, unit):
    radius = float(radius)
    try:
        if unit == "meters":
            earthradius = 6378.1
            radius = radius / 1000
        elif unit == "miles":
            earthradius = 3963.2
        else:
            earthradius = 6378.1
    except Exception as e:
        print("Error: ", e)
    finally:
        radians = radius / earthradius
        print("radians: ", radians)
    return radians


def get_meters(radius, unit):
    radius = int(radius)
    if unit == "meters":
        return radius
    elif unit == "mile":
        return radius * 1609.34
    else:
        return radius * 1000


def get_crimecounts_forlocation(coordinates, data, distance):
    Model.create_index([("point", "2dsphere")])

    # Return counts of documents
    count = Model.objects.all().count()
    print("count", count)

    longitude = coordinates[0]
    latitude = coordinates[1]

    pipeline = [
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "distanceField": "point",
                "maxDistance": distance,
                "spherical": True
            }
        }
    ]

    result = Model.objects().aggregate(*pipeline)
    distance_near_list = [doc['INCIDENT_NO'] for doc in result]

    if len(distance_near_list) != 0:
        print("distance_near_list", distance_near_list)
    else:
        print("query does not return a result", distance_near_list)
    return len(distance_near_list)


def create_dataframe(rowlist, collist, countlist, centerlist):
    print("create_dataframe")
    data = {'rows': rowlist, 'cols': collist, 'countlist': countlist, 'centerlist': centerlist}
    return data


def compute_range_percentage(count, countlist):
    arr = np.array(countlist)
    if count in range(0, 4):
        arr_range = (arr >= 0) & (arr <= 4)
        safe_percentage = np.sum(arr[arr_range])
        return ["safest", safe_percentage]
    elif count in range(5, 10):
        arr_range = (arr >= 5) & (arr <= 10)
        moderate_percentage = np.sum(arr[arr_range])
        return ["moderate", moderate_percentage]
    elif count in range(10, max(arr)):
        arr_range = (arr >= 10) & (arr <= max(arr))
        heavy_percentage = np.sum(arr[arr_range])
        return ["heaviest", heavy_percentage]

    # assign true to mid dle element in list else false


def get_middle_element_of_count_list(count_list):
    # if even
    if len(count_list) % 2 == 0:
        return (len(count_list) // 2) - 1
    else:
        return (len(count_list) - 1) // 2


def get_count_of_grid_histogram(polygon_dict, interval):
    start_time = time.time()
    sublists = [polygon_dict[i:i + 5] for i in range(0, len(polygon_dict), 5)]
    polygon_list = [search_within_polygon_histogram(sublist, interval) for sublist in sublists]
    print("polygon_list", polygon_list)
    print("--- %s secconds ---" % (time.time() - start_time))
    return polygon_list


def search_within_polygon_histogram(sublistelement, interval):
    polygon_pipeline = [
        {
            "$match": {
                "point": {
                    "$geoWithin": {
                        "$geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                sublistelement
                            ]
                        }
                    }
                }
            }
        }
    ]

    if interval == "12AM-3AM":
        result = IntervalOne.objects.aggregate(*polygon_pipeline)
        polygon_result_list = [doc for doc in result]
        if len(polygon_result_list) != 0:
            # print("foundsublist", sublistelement)
            print("polygon_result_list", len(polygon_result_list))
            return polygon_result_list
        else:
            # print("notfoundsublistelement", sublistelement)
            with open("not_found_sublist_elements.txt", "a") as file:
                file.write(f"notfoundsublistelement: {sublistelement}\n")
            return 0
    elif interval == "4AM-7AM":
        result = IntervalTwo.objects.aggregate(*polygon_pipeline)
        polygon_result_list = [doc for doc in result]
        print("polygon_result_list", polygon_result_list)
        if len(polygon_result_list) != 0:
            print("len_polygon_result_list", len(polygon_result_list))
            return polygon_result_list
        else:
            return 0
    elif interval == "8AM-11AM":
        result = IntervalThree.objects.aggregate(*polygon_pipeline)
        polygon_result_list = [doc for doc in result]
        if len(polygon_result_list) != 0:
            print("polygon_result_list", len(polygon_result_list))
            return polygon_result_list
        else:
            return 0
    elif interval == "12PM-3PM":
        result = IntervalFour.objects.aggregate(*polygon_pipeline)
        polygon_result_list = [doc for doc in result]
        if len(polygon_result_list) != 0:
            print("polygon_result_list", len(polygon_result_list))
            return polygon_result_list
        else:
            return 0
    elif interval == "4PM-7PM":
        result = IntervalFive.objects.aggregate(*polygon_pipeline)
        polygon_result_list = [doc for doc in result]
        if len(polygon_result_list) != 0:
            print("polygon_result_list", len(polygon_result_list))
            return polygon_result_list
        else:
            return 0
    elif interval == "8PM-11PM":
        result = IntervalSix.objects.aggregate(*polygon_pipeline)
        polygon_result_list = [doc for doc in result]
        if len(polygon_result_list) != 0:
            print("polygon_result_list", len(polygon_result_list))
            return polygon_result_list
        else:
            return 0
    else:
        # All intervals
        # element = [e for e in Model.objects()]
        # print("First element", element[0])
        result = Model.objects.aggregate(*polygon_pipeline)
        polygon_result_list = [doc for doc in result]
        if len(polygon_result_list) != 0:
            print("foundsublistelement", sublistelement)
            print("polygon_result_list", polygon_result_list)
            return polygon_result_list
        else:
            # print("notfoundelement", sublistelement)
            return 0


def get_count_of_grid_heatmap(polygon_dict, interval):
    print("Calling get_count_of_grid_heatmap")
    start_time = time.time()
    sublists = [polygon_dict[i:i + 5] for i in range(0, len(polygon_dict), 5)]
    count_list = [search_within_polygon_heatmap(sublist, interval) for sublist in sublists]
    print("count_list", count_list)
    print("--- %s secconds ---" % (time.time() - start_time))
    return count_list


def search_within_polygon_heatmap(sublistelement, interval):
    # start_time = time.time()
    polygon_pipeline = [
        {
            "$match": {
                "point": {
                    "$geoWithin": {
                        "$geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                sublistelement
                            ]
                        }
                    }
                }
            }
        }
    ]

    if interval == "12AM-3AM":
        result = IntervalOne.objects.aggregate(*polygon_pipeline)
        polygon_result_list = [doc for doc in result]
        if len(polygon_result_list) != 0:
            print("new_data_list", polygon_result_list[0])
            print("polygon_result_list", len(polygon_result_list))
        return len(polygon_result_list)
    elif interval == "4AM-7AM":
        result = IntervalTwo.objects.aggregate(*polygon_pipeline)
        polygon_result_list = [doc for doc in result]
        if len(polygon_result_list) != 0:
            print("new_data_list", polygon_result_list[0])
            print("polygon_result_list", len(polygon_result_list))
        return len(polygon_result_list)
    elif interval == "8AM-11AM":
        result = IntervalThree.objects.aggregate(*polygon_pipeline)
        polygon_result_list = [doc for doc in result]
        if len(polygon_result_list) != 0:
            print("new_data_list", polygon_result_list[0])
            print("polygon_result_list", len(polygon_result_list))
        return len(polygon_result_list)
    elif interval == "12PM-3PM":
        result = IntervalFour.objects.aggregate(*polygon_pipeline)
        polygon_result_list = [doc for doc in result]
        if len(polygon_result_list) != 0:
            print("new_data_list", polygon_result_list[0])
            print("polygon_result_list", len(polygon_result_list))
        return len(polygon_result_list)
    elif interval == "4PM-7PM":
        result = IntervalFive.objects.aggregate(*polygon_pipeline)
        polygon_result_list = [doc for doc in result]
        if len(polygon_result_list) != 0:
            print("new_data_list", polygon_result_list[0])
            print("polygon_result_list", len(polygon_result_list))
        return len(polygon_result_list)
    elif interval == "8PM-11PM":
        result = IntervalSix.objects.aggregate(*polygon_pipeline)
        polygon_result_list = [doc for doc in result]
        if len(polygon_result_list) != 0:
            print("new_data_list", polygon_result_list[0])
            print("polygon_result_list", len(polygon_result_list))
        return len(polygon_result_list)
    else:
        # All intervals
        result = Model.objects.aggregate(*polygon_pipeline)
        polygon_result_list = [doc for doc in result]
        if len(polygon_result_list) != 0:
            print("returned sublist element", sublistelement)
            print("new_data_list", polygon_result_list[0])
            print("polygon_result_list", len(polygon_result_list))
        return len(polygon_result_list)


def reverse_coordinates(geojson):
    reversed_list = []
    listcount = 0
    feature = geojson['features']

    for f in feature:
        geometry = f['geometry']
        coordinates = geometry['coordinates']
        for inner_list in coordinates:
            for item in inner_list:
                # reversed_list.append(item[::-1])
                reversed_list.append(item)
                listcount += 1
        [reversed_list[listcount: (1 + listcount) * 5]]

    return reversed_list


def create_grid2(cell_size_meters):
    min_lon, min_lat = -84.8192049318631, 39.0533271607855
    max_lon, max_lat = -84.2545822217415, 39.3599982625544

    transformer4326 = Transformer.from_crs("EPSG:4326", "EPSG:3857")
    transformer3857 = Transformer.from_crs("EPSG:3857", "EPSG:4326")

    min_x, min_y = transformer4326.transform(min_lon, min_lat)
    max_x, max_y = transformer4326.transform(max_lon, max_lat)

    bbox_3857 = (min_x, min_y, max_x, max_y)

    # Calculate the size of each grid cell in EPSG:3857
    width_3857 = bbox_3857[2] - bbox_3857[0]
    height_3857 = bbox_3857[3] - bbox_3857[1]

    # Calculate the number of rows and columns
    num_rows = int(height_3857 / cell_size_meters)
    num_cols = int(width_3857 / cell_size_meters)

    cell_width_3857 = width_3857 / num_cols
    cell_height_3857 = height_3857 / num_rows

    # Create a grid of squares
    grid = []
    for i in range(num_rows):
        for j in range(num_cols):
            # Calculate the coordinates of the current grid cell in EPSG:3857
            x_min = bbox_3857[0] + j * cell_width_3857
            y_min = bbox_3857[1] + i * cell_height_3857
            x_max = x_min + cell_width_3857
            y_max = y_min + cell_height_3857

            x_min_4326, y_min_4326 = transformer3857.transform(x_min, y_min)
            x_max_4326, y_max_4326 = transformer3857.transform(x_max, y_max)

            # Create a Shapely geometry box for the current grid cell in EPSG:4326
            cell_4326 = box(x_min_4326, y_min_4326, x_max_4326, y_max_4326)

            # Append the geometry box to the grid
            grid.append(cell_4326)

    # Create a GeoDataFrame from the grid cells
    grid_gdf = gpd.GeoDataFrame(geometry=grid, crs="EPSG:4326")

    return grid_gdf


def create_grid(cell_size_meters):
    epsg4326 = Proj(init='EPSG:4326')
    epsg3857 = Proj(init='EPSG:3857')

    min_lon, min_lat = -84.8192049318631, 39.0533271607855
    max_lon, max_lat = -84.2545822217415, 39.3599982625544

    # Transform the bounding box to EPSG:3857
    min_x, min_y = transform(epsg4326, epsg3857, min_lon, min_lat)
    max_x, max_y = transform(epsg4326, epsg3857, max_lon, max_lat)
    bbox_3857 = (min_x, min_y, max_x, max_y)

    # Calculate the size of each grid cell in EPSG:3857
    width_3857 = bbox_3857[2] - bbox_3857[0]
    height_3857 = bbox_3857[3] - bbox_3857[1]

    # print("width_3857", width_3857)
    # print("height_3857", height_3857)

    # Calculate the number of rows and columns
    num_rows = int(height_3857 / cell_size_meters)
    num_cols = int(width_3857 / cell_size_meters)

    # print("num_rows",num_rows)
    # print("num_cols",num_cols)

    cell_width_3857 = width_3857 / num_cols
    cell_height_3857 = height_3857 / num_rows

    # print("cell_width_3857",cell_width_3857)
    # print("cell_height_3857",cell_height_3857)

    # Create a grid of squares
    grid = []
    for i in range(num_rows):
        for j in range(num_cols):
            # Calculate the coordinates of the current grid cell in EPSG:3857
            x_min = bbox_3857[0] + j * cell_width_3857
            y_min = bbox_3857[1] + i * cell_height_3857
            x_max = x_min + cell_width_3857
            y_max = y_min + cell_height_3857

            # Transform the EPSG:3857 coordinates back to EPSG:4326
            x_min_4326, y_min_4326 = transform(epsg3857, epsg4326, x_min, y_min)
            x_max_4326, y_max_4326 = transform(epsg3857, epsg4326, x_max, y_max)

            # Create a Shapely geometry box for the current grid cell in EPSG:4326
            cell_4326 = box(x_min_4326, y_min_4326, x_max_4326, y_max_4326)

            # Append the geometry box to the grid
            grid.append(cell_4326)

    # Create a GeoDataFrame from the grid cells
    grid_gdf = gpd.GeoDataFrame(geometry=grid, crs="EPSG:4326")

    return grid_gdf


def create_interval_for_dial(grid):
    # return unique elements from list
    grid_set = set(grid)
    sorted_grid_set = sorted(grid_set)
    number_of_intervals = 3
    split_data = np.array_split(sorted_grid_set, number_of_intervals)
    return split_data


def create_bounding_box(latitude, longitude, distance):
    deg_per_meter_lat = 1 / 111320  # Approx. 1 degree latitude = 111.32 km
    lat_diff = distance * deg_per_meter_lat

    deg_per_meter_lon = 1 / (111320 * math.cos(math.radians(latitude)))
    lon_diff = distance * deg_per_meter_lon

    return {
        "west": longitude - lon_diff,
        "east": longitude + lon_diff,
        "south": latitude - lat_diff,
        "north": latitude + lat_diff
    }


def create_grid_heatmap_new(distance, latitude, longitude):
    print("latitude", latitude)
    print("longitude", longitude)
    # Transform the bounding box to EPSG:3857
    # from point compute bounding box using distance

    transformer_to_3857 = Transformer.from_crs("EPSG:4326", "EPSG:3857")
    transformer_to_4326 = Transformer.from_crs("EPSG:3857", "EPSG:4326")

    # Transform the point to EPSG:3857
    transformed_point_coordinates = transformer_to_3857.transform(latitude, longitude)

    grid_size = 5
    half_grid_size = grid_size // 2

    # Create a grid of squares
    grid = []
    for i in range(-half_grid_size, half_grid_size + 1):
        for j in range(-half_grid_size, half_grid_size + 1):
            min_x = transformed_point_coordinates[1] + (i * distance)
            min_y = transformed_point_coordinates[0] + (j * distance)
            max_x = min_x + distance
            max_y = min_y + distance

            # Transform the EPSG:3857 coordinates back to EPSG:4326
            min_lon, min_lat = transformer_to_4326.transform(min_y, min_x)
            max_lon, max_lat = transformer_to_4326.transform(max_y, max_x)

            # Create a Shapely geometry box for the current grid cell in EPSG:4326
            cell_4326 = box(min_lat, min_lon, max_lat, max_lon)
            grid.append(cell_4326)

    # Create a GeoDataFrame from the grid cells
    grid_gdf = gpd.GeoDataFrame(geometry=grid, crs="EPSG:4326")

    return grid_gdf


# new function updated with bbox
# Function to create grid heatmap based on transformed bounding box
def create_grid_heatmap_new_bbox(distance, latitude, longitude):
    print("latitude", latitude)
    print("longitude", longitude)

    # Calculate bounding box using the create_bounding_box function
    bbox = create_bounding_box(latitude, longitude, distance)

    # Extract the bounding box coordinates
    min_lat = bbox["south"]
    max_lat = bbox["north"]
    min_lon = bbox["west"]
    max_lon = bbox["east"]

    print("Bounding box:", bbox)

    # Create transformers for coordinate conversions
    transformer_to_3857 = Transformer.from_crs("EPSG:4326", "EPSG:3857")
    transformer_to_4326 = Transformer.from_crs("EPSG:3857", "EPSG:4326")

    # Transform the bounding box coordinates to EPSG:3857
    min_x, min_y = transformer_to_3857.transform(min_lat, min_lon)
    max_x, max_y = transformer_to_3857.transform(max_lat, max_lon)

    grid_size = 5
    half_grid_size = grid_size // 2

    # Create a grid of squares
    grid = []
    for i in range(-half_grid_size, half_grid_size + 1):
        for j in range(-half_grid_size, half_grid_size + 1):
            cell_min_x = min_x + (i * distance)
            cell_min_y = min_y + (j * distance)
            cell_max_x = cell_min_x + distance
            cell_max_y = cell_min_y + distance

            # Transform the EPSG:3857 coordinates back to EPSG:4326
            min_lon, min_lat = transformer_to_4326.transform(cell_min_y, cell_min_x)
            max_lon, max_lat = transformer_to_4326.transform(cell_max_y, cell_max_x)

            # Create a Shapely geometry box for the current grid cell in EPSG:4326
            cell_4326 = box(min_lon, min_lat, max_lon, max_lat)
            grid.append(cell_4326)

    # Create a GeoDataFrame from the grid cells
    grid_gdf = gpd.GeoDataFrame(geometry=grid, crs="EPSG:4326")

    return grid_gdf


def create_heatmap_polygon(distance, point):
    grid = create_grid_heatmap_new(distance, point[1][0], point[1][1])
    grid_geojson = grid.to_json()
    grid_geojson_parsed = json.loads(grid_geojson)
    polygon = reverse_coordinates(grid_geojson_parsed)
    return polygon


def delete_heatmap_files():
    data_folder = "data"

    heatmap_folder = "heatmap"

    heatmap_files = [
        "heatmap_data_safe.csv",
        "heatmap_data_work.csv",
        "heatmap_data_current.csv",
        "heatmap_data_destination.csv"
    ]

    deleted_files = []
    errors = []

    for file in heatmap_files:
        file_path = os.path.join(PROJECT_DIR, data_folder, heatmap_folder, file)
        print("file_path", file_path)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_files.append(file)
            else:
                errors.append(f"{file} does not exist")
        except Exception as e:
            errors.append(f"Error deleting {file}: {str(e)}")


@app.route('/deleteheatmapfile')
def delete_heatmap_file_endpoint():
    # os join base folder with data folder
    # iterate through files in folder and delete

    data_folder = "data"
    heatmap_folder = "heatmap"

    heatmap_files = [
        "heatmap_data_safe.csv",
        "heatmap_data_work.csv",
        "heatmap_data_current.csv",
        "heatmap_data_destination.csv"
    ]

    deleted_files = []
    errors = []

    for file in heatmap_files:
        file_path = os.path.join(PROJECT_DIR, data_folder, heatmap_folder, file)
        print("file_path", file_path)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_files.append(file)
            else:
                errors.append(f"{file} does not exist")
        except Exception as e:
            errors.append(f"Error deleting {file}: {str(e)}")

    return jsonify({
        'deleted_files': deleted_files,
        'errors': errors
    }), 200


@app.route('/deletefilteredmodels')
def delete_filtered_models():
    try:
        if IntervalOne.objects().first():
            deleted_count1 = IntervalOne.objects().delete()
        if IntervalTwo.objects().first():
            deleted_count2 = IntervalTwo.objects().delete()
        if IntervalThree.objects().first():
            deleted_count3 = IntervalThree.objects().delete()
        if IntervalFour.objects().first():
            deleted_count4 = IntervalFour.objects().delete()
        if IntervalFive.objects().first():
            deleted_count5 = IntervalFive.objects().delete()
        if IntervalSix.objects().first():
            deleted_count6 = IntervalSix.objects().delete()
        return jsonify({"status": "success", "deleted_count": deleted_count1,
                        "status": "success", "deleted_count": deleted_count2,
                        "status": "success", "deleted_count": deleted_count3,
                        "status": "success", "deleted_count": deleted_count4,
                        "status": "success", "deleted_count": deleted_count5,
                        "status": "success", "deleted_count": deleted_count6,
                        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/createfilteredmodels')
def create_filtered_models():
    try:
        interval_list = [
            "12AM-3AM",
            # "4AM-7AM",
            #  "8AM-11AM",
            #  "12PM-3PM",
            #  "4PM-7PM",
            #  "8PM-11PM",
            "All"
        ]

        hour_aggregate_data = load_dataset2()
        for interval in interval_list:
            data = filter_dataset(interval, hour_aggregate_data)
            filtered_data_list = [doc for doc in data if
                                  doc.get("INCIDENT_NO") is not None and isinstance(doc["INCIDENT_NO"], str)]
            if interval == "12AM-3AM":
                for doc in filtered_data_list:
                    new_model_instance = IntervalOne(**doc)
                    new_model_instance.save()
            elif interval == "4AM-7AM":
                for doc in filtered_data_list:
                    new_model_instance = IntervalTwo(**doc)
                    new_model_instance.save()
            elif interval == "8AM-11AM":
                for doc in filtered_data_list:
                    new_model_instance = IntervalThree(**doc)
                    new_model_instance.save()
            elif interval == "12PM-3PM":
                for doc in filtered_data_list:
                    new_model_instance = IntervalFour(**doc)
                    new_model_instance.save()
            elif interval == "4PM-7PM":
                for doc in filtered_data_list:
                    new_model_instance = IntervalFive(**doc)
                    new_model_instance.save()
            elif interval == "8PM-11PM":
                for doc in filtered_data_list:
                    new_model_instance = IntervalSix(**doc)
                    new_model_instance.save()
            else:
                print("Update model with filtered data results")
                for doc in filtered_data_list:
                    new_model_instance = FilteredModel(**doc)
                    new_model_instance.save()

        return jsonify({"status": "success", "message": 200})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def get_data(response, filename):
    json_str = response.get_data(as_text=True)
    python_dict = json.loads(json_str)
    print("python_dict", python_dict)
    # flattened list
    data_not_none_list = [d for sublist in python_dict for d in (sublist if isinstance(sublist, list) else [sublist]) if
                          d != 0]
    data_none_list = [element for element in python_dict if element == 0]
    print("data_not_none_list", data_not_none_list)

    neighborhood_result_list = []
    for element in data_not_none_list:
        print("ELEMENT", element)

        if isinstance(element, dict) and 'CPD_NEIGHBORHOOD' in element:
            neighborhood_result_list.append(element['CPD_NEIGHBORHOOD'])
    print("neighborhood_result_list", neighborhood_result_list)
    # group counts by the neighborhood
    set_neighborhood_result_list = set(neighborhood_result_list)
    print("set_neighborhood_result_list", set_neighborhood_result_list)

    filtered_count_list = []
    for k in set_neighborhood_result_list:
        filtered_list = [element for element in data_not_none_list if element.get('CPD_NEIGHBORHOOD') == k]
        print("filtered_list", filtered_list)
        filtered_count = len(filtered_list)
        filtered_count_list.append(filtered_count)

    print("data_none_list", data_none_list)
    print("filtered_count_list", filtered_count_list)

    appended_list = data_none_list + filtered_count_list
    new_neighborhood_list = list(set_neighborhood_result_list)

    print("appended_list", appended_list)

    datajson = {
        "appended_list": appended_list,
        "new_neighborhood_list": new_neighborhood_list
    }

    file_name = os.path.join(PROJECT_DIR, "static", "data", "histogram", filename + ".json")

    # Write JSON data to a file
    if datajson:
        with open(file_name, 'w') as file:
            json.dump(datajson, file, indent=4)
    else:
        print("data not created")

    return datajson


@app.route('/createnewgrids')
def create_new_grids():
    # call create_grids(element)
    # element is tuplecle
    # return response files created

    create_grids((700, "meters", "All"))
    # create_grids((700, "meters", "12AM-3AM"))
    # create_grids((700, "meters", "4AM-7AM"))
    # create_grids((700, "meters", "8AM-11AM"))
    # create_grids((700, "meters", "12PM-3PM"))
    # create_grids((700, "meters", "4PM-7PM"))
    # create_grids((700, "meters", "8PM-11PM"))
    # create_grids((750, "meters", "All"))
    # create_grids((750, "meters", "12AM-3AM"))
    # create_grids((750, "meters", "4AM-7AM"))
    # create_grids((750, "meters", "8AM-11AM"))
    # create_grids((750, "meters", "12PM-3PM"))
    # create_grids((750, "meters", "4PM-7PM"))
    # create_grids((750, "meters", "8PM-11PM"))
    # create_grids((800, "meters", "All"))
    # create_grids((800, "meters", "12AM-3AM"))
    # create_grids((800, "meters", "4AM-7AM"))
    # create_grids((800, "meters", "8AM-11AM"))
    # create_grids((800, "meters", "12PM-3PM"))
    # create_grids((800, "meters", "4PM-7PM"))
    # create_grids((800, "meters", "8PM-11PM"))
    # create_grids((850, "meters", "All"))
    # create_grids((850, "meters", "12AM-3AM"))
    # create_grids((850, "meters", "4AM-7AM"))
    # create_grids((850, "meters", "8AM-11AM"))
    # create_grids((850, "meters", "12PM-3PM"))
    # create_grids((850, "meters", "4PM-7PM"))
    # create_grids((850, "meters", "8PM-11PM"))
    # create_grids((900, "meters", "All"))
    # create_grids((900, "meters", "12AM-3AM"))
    # create_grids((900, "meters", "4AM-7AM"))
    # create_grids((900, "meters", "8AM-11AM"))
    # create_grids((900, "meters", "12PM-3PM"))
    # create_grids((900, "meters", "4PM-7PM"))
    # create_grids((900, "meters", "8PM-11PM"))
    # create_grids((950, "meters", "All"))
    # create_grids((950, "meters", "12AM-3AM"))
    # create_grids((950, "meters", "4AM-7AM"))
    # create_grids((950, "meters", "8AM-11AM"))
    # create_grids((950, "meters", "12PM-3PM"))
    # create_grids((950, "meters", "4PM-7PM"))
    # create_grids((950, "meters", "8PM-11PM"))
    # create_grids((1, "kilometer", "All"))
    # create_grids((1, "kilometer", "12AM-3AM"))
    # create_grids((1, "kilometer", "4AM-7AM"))
    # create_grids((1, "kilometer", "8AM-11AM"))
    # create_grids((1, "kilometer", "12PM-3PM"))
    # create_grids((1, "kilometer", "4PM-7PM"))
    # create_grids((1, "kilometer", "8PM-11PM"))
    # create_grids((1, "mile", "All"))
    # create_grids((1, "mile", "12AM-3AM"))
    # create_grids((1, "mile", "4AM-7AM"))
    # create_grids((1, "mile", "8AM-11AM"))
    # create_grids((1, "mile", "12PM-3PM"))
    # create_grids((1, "mile", "4PM-7PM"))
    # create_grids((1, "mile", "8PM-11PM"))

    return "Files Created", 200


def create_grids(element):
    polygon_list = []

    file_name = str(element[0]) + element[1] + element[2]

    distance = get_meters(element[0], element[1])
    print("distance", distance)
    grid = create_grid2(distance)
    interval = element[2]
    grid_geojson = grid.to_json()
    grid_geojson_parsed = json.loads(grid_geojson)
    polygon = reverse_coordinates(grid_geojson_parsed)
    # print("polygon", polygon)
    polygon_list.append(polygon)

    # TODO Need to fix the performance - function is called twice
    data_list = get_count_of_grid_histogram(polygon, interval)

    json_data_list = jsonify(data_list)

    return get_data(json_data_list, file_name)


# Model add hour field aggregate to police_cinci_data_new
# filter out where point = [0,0]
# Filter out offense list
# iterate through result list and save to new model
# from the new model filter by the interval then apply the polygon_pipeline


@app.route('/testgrids')
def test_grids():
    distance = get_meters(950, "meters")
    grid = create_grid2(distance)
    grid_geojson = grid.to_json()
    grid_geojson_parsed = json.loads(grid_geojson)
    print("grid_geojson_parsed", grid_geojson_parsed)

    return render_template('gridmap.html', polygon=grid_geojson_parsed, key=key)


@app.route('/testheatmapgrid')
def test_heatmap_grid():
    point = (39.1318613, -84.51576195582436)
    distance = get_meters(700, "meters")
    grid = create_grid_heatmap_new(distance, point[0], point[1])
    grid_geojson = grid.to_json()
    grid_geojson_parsed = json.loads(grid_geojson)

    return render_template('gridmap.html', polygon=grid_geojson_parsed, key=key)


@app.route('/success/<safe>/<work>/<current>/<destination>/<interval>/<gridsize>')
def success(safe, work, current, destination, interval, gridsize):
    geolocator = Nominatim(user_agent="project-flask")
    # delete_heatmap_files()
    try:
        safelocation = geolocator.geocode(safe)
        worklocation = geolocator.geocode(work)
        currentlocation = geolocator.geocode(current)
        destinationlocation = geolocator.geocode(destination)
        user = UserData()
        user.add_safe_coordinates(safelocation.latitude, safelocation.longitude)
        print("safecoordinates", user.safecoordinates)

        user.add_work_coordinates(worklocation.latitude, worklocation.longitude)
        print("workcoordinates", user.workcoordinates)

        user.add_current_coordinates(currentlocation.latitude, currentlocation.longitude)
        print("currentcoordinates", user.currentcoordinates)

        user.add_destination_coordinates(destinationlocation.latitude, destinationlocation.longitude)
        print("destinationcoordinates", user.destinationcoordinates)

        gridsplit = gridsize.split()
        radius = gridsplit[0]
        unit = gridsplit[1]

        print("gridsize", gridsize)
        selected_grid = switch_grids2(gridsize, interval)
        print("selected_grid", selected_grid)

        # file_name = os.path.join(PROJECT_DIR, 'static', 'data', 'histogram', '700metersAll.json')
        #
        # try:
        #     # Open and read the JSON file
        #     with open(file_name, 'r') as file:
        #         datajson = json.load(file)
        #
        #     # Access the appended_list
        #     appended_list = datajson.get("appended_list", [])
        #     return jsonify({"appended_list": appended_list})
        # except FileNotFoundError:
        #     return jsonify({"error": "File not found"}), 404
        # except json.JSONDecodeError:
        #     return jsonify({"error": "Error decoding JSON"}), 400

        user.interval = interval
        user.radius = radius
        user.units = unit
        user.grid = selected_grid

        aggregate_data = load_dataset()
        data = filter_dataset(user.interval, aggregate_data)
        filtered_data_list = [doc for doc in data]

        meters = get_meters(user.radius, user.units)

        # Will comment out block
        countsafe = get_crimecounts_forlocation(user.safecoordinates, filtered_data_list, meters)
        countwork = get_crimecounts_forlocation(user.workcoordinates, filtered_data_list, meters)
        countcurrent = get_crimecounts_forlocation(user.currentcoordinates, filtered_data_list, meters)
        countdestination = get_crimecounts_forlocation(user.destinationcoordinates, filtered_data_list, meters)
        print("countsafe", countsafe, "countwork", countwork, "countcurrent", countcurrent, "countdestination",
              countdestination)

        safepolygon = create_heatmap_polygon(meters, safelocation)
        workpolygon = create_heatmap_polygon(meters, worklocation)
        currentpolygon = create_heatmap_polygon(meters, currentlocation)
        destinationpolygon = create_heatmap_polygon(meters, destinationlocation)

        safe_count_list = get_count_of_grid_heatmap(safepolygon, user.interval)
        work_count_list = get_count_of_grid_heatmap(workpolygon, user.interval)
        current_count_list = get_count_of_grid_heatmap(currentpolygon, user.interval)
        destination_count_list = get_count_of_grid_heatmap(destinationpolygon, user.interval)

        middle_index = get_middle_element_of_count_list(safe_count_list)
        conditional_safe_center_point_list = [True if index == middle_index else
                                              False for index, num in enumerate(safe_count_list)]
        middle_element_safe_count = safe_count_list[middle_index]
        print("middle_element_safe_count", middle_element_safe_count)

        middle_index = get_middle_element_of_count_list(work_count_list)
        conditional_work_center_point_list = [True if index == middle_index else
                                              False for index, num in enumerate(work_count_list)]
        middle_element_work_count = work_count_list[middle_index]
        print("middle_element_work_count", middle_element_work_count)

        middle_index = get_middle_element_of_count_list(current_count_list)
        conditional_current_center_point_list = [True if index == middle_index else
                                                 False for index, num in enumerate(current_count_list)]
        middle_element_current_count = current_count_list[middle_index]
        print("middle_element_current_count", middle_element_current_count)

        middle_index = get_middle_element_of_count_list(destination_count_list)
        conditional_destination_center_point_list = [True if index == middle_index else
                                                     False for index, num in enumerate(destination_count_list)]
        middle_element_destination_count = destination_count_list[middle_index]
        print("middle_element_destination_count", middle_element_destination_count)

        print("conditional_safe_center_point_list", conditional_safe_center_point_list)

        current_all_interval_count_list = []
        # generate list of middle elements for all current counts. Iterate through the list of intervals
        interval_list = ["12AM-3AM",
                         "4AM-7AM",
                         "8AM-11AM",
                         "12PM-3PM",
                         "4PM-7PM",
                         "8PM-11PM"]

        for i in interval_list:
            current_count_list = get_count_of_grid_heatmap(currentpolygon, i)
            # get middle element of current_count_list
            middle_element_current_count = current_count_list[middle_index]
            current_all_interval_count_list.append(middle_element_current_count)

        print("current_all_interval_count_list", current_all_interval_count_list)
        print("interval_list", interval_list)
        bounding_box_safe = create_bounding_box(user.safecoordinates[1], user.safecoordinates[0], meters)
        bounding_box_current = create_bounding_box(user.currentcoordinates[1], user.currentcoordinates[0], meters)
        bounding_box_work = create_bounding_box(user.workcoordinates[1], user.workcoordinates[0], meters)
        bounding_box_destination = create_bounding_box(user.destinationcoordinates[1], user.destinationcoordinates[0],
                                                       meters)

        interval_lists = create_interval_for_dial(user.grid)
        interval_list1 = interval_lists[0]
        interval_list2 = interval_lists[1]
        interval_list3 = interval_lists[2]

        print("bounding_box_safe", bounding_box_safe)
        print("bounding_box_current", bounding_box_current)
        print("bounding_box_work", bounding_box_work)
        print("bounding_box_destination", bounding_box_destination)

        rows_list = ["A", "A", "A", "A", "A", "B", "B", "B", "B", "B", "C", "C", "C", "C", "C", "D", "D", "D", "D", "D",
                     "E", "E", "E", "E", "E"]
        col_list = ["v1", "v2", "v3", "v4", "v5", "v1", "v2", "v3", "v4", "v5", "v1", "v2", "v3", "v4", "v5",
                    "v1", "v2", "v3", "v4", "v5", "v1", "v2", "v3", "v4", "v5"]

        safe_dataframe = create_dataframe(rows_list, col_list, safe_count_list, conditional_safe_center_point_list)
        print("safe_dataframe", safe_dataframe)

        work_dataframe = create_dataframe(rows_list, col_list, work_count_list, conditional_work_center_point_list)
        print("work_dataframe", work_dataframe)

        current_dataframe = create_dataframe(rows_list, col_list, current_count_list,
                                             conditional_current_center_point_list)
        print("current_dataframe", current_dataframe)

        destination_dataframe = create_dataframe(rows_list, col_list, destination_count_list,
                                                 conditional_destination_center_point_list)
        # print("destination_dataframe", destination_dataframe)

        df_safe = pd.DataFrame(safe_dataframe)
        df_work = pd.DataFrame(work_dataframe)
        df_current = pd.DataFrame(current_dataframe)
        df_destination = pd.DataFrame(destination_dataframe)

        # Convert created DataFrame to CSV
        df_safe.to_csv('static/data/heatmap/heatmap_data_safe.csv', index=False)
        df_work.to_csv('static/data/heatmap/heatmap_data_work.csv', index=False)
        df_current.to_csv('static/data/heatmap/heatmap_data_current.csv', index=False)
        df_destination.to_csv('static/data/heatmap/heatmap_data_destination.csv', index=False)

        safe_statistic = compute_range_percentage(middle_element_safe_count, safe_count_list)
        current_statistic = compute_range_percentage(middle_element_current_count, current_count_list)
        work_statistic = compute_range_percentage(middle_element_work_count, work_count_list)
        destination_statistic = compute_range_percentage(middle_element_destination_count, destination_count_list)

        safe_percentage, safe_text = safe_statistic[1], safe_statistic[0]
        current_percentage, current_text = current_statistic[1], current_statistic[0]
        work_percentage, work_text = work_statistic[1], work_statistic[0]
        destination_percentage, destination_text = destination_statistic[1], destination_statistic[0]

        print("safe_percentage", safe_percentage)
        print("current_percentage", current_percentage)
        print("work_percentage", work_percentage)
        print("destination_percentage", destination_percentage)
        print("interval", interval)

        # number_of_years = get_difference_in_years()
        # print("number_of_years",number_of_years)

        return render_template('success.html', key=key, grid=user.grid, maxgridelement=max(user.grid),
                               radius=user.radius, interval=user.interval,
                               years=13,
                               latsafecoordinate=user.safecoordinates[1],
                               lonsafecoordinate=user.safecoordinates[0],
                               latcurrentcoordinate=user.currentcoordinates[1],
                               loncurrentcoordinate=user.currentcoordinates[0],
                               latworkcoordinate=user.workcoordinates[1],
                               lonworkcoordinate=user.workcoordinates[0],
                               latdestinationcoordinate=user.destinationcoordinates[1],
                               londestinationcoordinate=user.destinationcoordinates[0],
                               middle_element_safe_count=middle_element_safe_count,
                               middle_element_current_count=middle_element_current_count,
                               middle_element_work_count=middle_element_work_count,
                               middle_element_destination_count=middle_element_destination_count,
                               bounding_box_safe=bounding_box_safe,
                               bounding_box_current=bounding_box_current,
                               bounding_box_work=bounding_box_work,
                               bounding_box_destination=bounding_box_destination,
                               intervalOne=interval_list1,
                               intervalTwo=interval_list2,
                               intervalThree=interval_list3,
                               safe_percentage=safe_percentage,
                               current_percentage=current_percentage,
                               work_percentage=work_percentage,
                               destination_percentage=destination_percentage,
                               safe_text=safe_text,
                               current_text=current_text,
                               work_text=work_text,
                               destination_text=destination_text,
                               current_all_interval_count_list=current_all_interval_count_list,
                               interval_list=interval_list
                               )
    except GeocoderTimedOut as e:
        return render_template('404.html'), 404


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        safe = request.form.get("safe")
        work = request.form.get("work")
        current = request.form.get("current")
        destination = request.form.get("destination")
        interval = request.form.get("interval")
        gridsize = request.form.get("gridsize")

        return redirect(url_for('success', safe=safe, work=work, current=current, destination=destination,
                                interval=interval, gridsize=gridsize))

    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
