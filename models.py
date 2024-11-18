from flask_mongoengine import MongoEngine
from bson import ObjectId, Binary
import json

db = MongoEngine()


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, Binary):
            return obj.hex()
        return super(CustomJSONEncoder, self).default(obj)


# data should be filtered by frontend user. Need to validate
class Model(db.DynamicDocument):
    id = db.ObjectIdField()
    INCIDENT_NO = db.StringField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    FLOOR = db.StringField()
    DAYOFWEEK = db.StringField()
    CPD_NEIGHBORHOOD = db.StringField()
    WEAPONS = db.StringField()
    DATE_OF_CLEARANCE = db.StringField()
    HOUR_FROM = db.IntField()
    HOUR_TO = db.IntField()
    ADDRESS_X = db.StringField()
    LONGITUDE_X = db.FloatField()
    LATITUDE_X = db.FloatField()
    point = db.PointField()
    year = db.StringField()
    day = db.StringField()
    month = db.StringField()
    time = db.StringField()
    hour = db.StringField()
    meta = {'collection': 'police_cinci_data_all',
            'strict': False}

    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "DAYOFWEEK": self.DAYOFWEEK,
            "CPD_NEIGHBORHOOD": self.CPD_NEIGHBORHOOD,
            "WEAPONS": self.WEAPONS,
            "DATE_OF_CLEARANCE": self.DATE_OF_CLEARANCE,
            "HOUR_FROM": self.HOUR_FROM,
            "HOUR_TO": self.HOUR_TO,
            "ADDRESS_X": self.ADDRESS_X,
            "LONGITUDE_X": self.LONGITUDE_X,
            "LATITUDE_X": self.LATITUDE_X,
            "point": self.point,
            "year": self.year,
            "day": self.day,
            "month": self.month,
            "time": self.time,
            "hour": self.hour
        }


# Used to filter Model based on interval and distance than on deletegrid endpoint data will be deleted for grid calculation
class IntervalOne(db.DynamicDocument):
    _id = db.ObjectIdField()
    INCIDENT_NO = db.StringField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    HATE_BIAS = db.StringField()
    DAYOFWEEK = db.StringField()
    CPD_NEIGHBORHOOD = db.StringField()
    WEAPONS = db.StringField()
    DATE_OF_CLEARANCE = db.StringField()
    HOUR_FROM = db.IntField()
    HOUR_TO = db.IntField()
    ADDRESS_X = db.StringField()
    LONGITUDE_X = db.FloatField()
    LATITUDE_X = db.FloatField()
    VICTIM_AGE = db.StringField()
    VICTIM_RACE = db.StringField()
    point = db.PointField()
    year = db.StringField()
    day = db.StringField()
    month = db.StringField()
    time = db.StringField()
    hour = db.StringField()
    meta = {'collection': 'police_cinci_data_interval_all_one',
            'strict': False}

    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "DAYOFWEEK": self.DAYOFWEEK,
            "CPD_NEIGHBORHOOD": self.CPD_NEIGHBORHOOD,
            "WEAPONS": self.WEAPONS,
            "DATE_OF_CLEARANCE": self.DATE_OF_CLEARANCE,
            "HOUR_FROM": self.HOUR_FROM,
            "HOUR_TO": self.HOUR_TO,
            "ADDRESS_X": self.ADDRESS_X,
            "LONGITUDE_X": self.LONGITUDE_X,
            "LATITUDE_X": self.LATITUDE_X,
            "point": self.point,
            "year": self.year,
            "day": self.day,
            "month": self.month,
            "time": self.time,
            "hour": self.hour
        }


class IntervalTwo(db.DynamicDocument):
    _id = db.ObjectIdField()
    INCIDENT_NO = db.StringField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    DAYOFWEEK = db.StringField()
    CPD_NEIGHBORHOOD = db.StringField()
    WEAPONS = db.StringField()
    DATE_OF_CLEARANCE = db.StringField()
    HOUR_FROM = db.IntField()
    HOUR_TO = db.IntField()
    ADDRESS_X = db.StringField()
    LONGITUDE_X = db.FloatField()
    LATITUDE_X = db.FloatField()
    VICTIM_AGE = db.StringField()
    VICTIM_RACE = db.StringField()
    point = db.PointField()
    year = db.StringField()
    day = db.StringField()
    month = db.StringField()
    time = db.StringField()
    hour = db.StringField()
    meta = {'collection': 'police_cinci_data_interval_all_two',
            'strict': False}

    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "DAYOFWEEK": self.DAYOFWEEK,
            "CPD_NEIGHBORHOOD": self.CPD_NEIGHBORHOOD,
            "WEAPONS": self.WEAPONS,
            "DATE_OF_CLEARANCE": self.DATE_OF_CLEARANCE,
            "HOUR_FROM": self.HOUR_FROM,
            "HOUR_TO": self.HOUR_TO,
            "ADDRESS_X": self.ADDRESS_X,
            "LONGITUDE_X": self.LONGITUDE_X,
            "LATITUDE_X": self.LATITUDE_X,
            "point": self.point,
            "year": self.year,
            "day": self.day,
            "month": self.month,
            "time": self.time,
            "hour": self.hour
        }


class IntervalThree(db.DynamicDocument):
    _id = db.ObjectIdField()
    INCIDENT_NO = db.StringField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    DAYOFWEEK = db.StringField()
    CPD_NEIGHBORHOOD = db.StringField()
    WEAPONS = db.StringField()
    DATE_OF_CLEARANCE = db.StringField()
    HOUR_FROM = db.IntField()
    HOUR_TO = db.IntField()
    ADDRESS_X = db.StringField()
    LONGITUDE_X = db.FloatField()
    LATITUDE_X = db.FloatField()
    VICTIM_AGE = db.StringField()
    VICTIM_RACE = db.StringField()
    point = db.PointField()
    year = db.StringField()
    day = db.StringField()
    month = db.StringField()
    time = db.StringField()
    hour = db.StringField()
    meta = {'collection': 'police_cinci_data_interval_all_three',
            'strict': False}

    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "DAYOFWEEK": self.DAYOFWEEK,
            "CPD_NEIGHBORHOOD": self.CPD_NEIGHBORHOOD,
            "WEAPONS": self.WEAPONS,
            "DATE_OF_CLEARANCE": self.DATE_OF_CLEARANCE,
            "HOUR_FROM": self.HOUR_FROM,
            "HOUR_TO": self.HOUR_TO,
            "ADDRESS_X": self.ADDRESS_X,
            "LONGITUDE_X": self.LONGITUDE_X,
            "LATITUDE_X": self.LATITUDE_X,
            "point": self.point,
            "year": self.year,
            "day": self.day,
            "month": self.month,
            "time": self.time,
            "hour": self.hour
        }


class IntervalFour(db.DynamicDocument):
    _id = db.ObjectIdField()
    INCIDENT_NO = db.StringField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    DAYOFWEEK = db.StringField()
    CPD_NEIGHBORHOOD = db.StringField()
    WEAPONS = db.StringField()
    DATE_OF_CLEARANCE = db.StringField()
    HOUR_FROM = db.IntField()
    HOUR_TO = db.IntField()
    ADDRESS_X = db.StringField()
    LONGITUDE_X = db.FloatField()
    LATITUDE_X = db.FloatField()
    VICTIM_AGE = db.StringField()
    VICTIM_RACE = db.StringField()
    point = db.PointField()
    year = db.StringField()
    day = db.StringField()
    month = db.StringField()
    time = db.StringField()
    hour = db.StringField()
    meta = {'collection': 'police_cinci_data_interval_all_four',
            'strict': False}


    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "DAYOFWEEK": self.DAYOFWEEK,
            "CPD_NEIGHBORHOOD": self.CPD_NEIGHBORHOOD,
            "WEAPONS": self.WEAPONS,
            "DATE_OF_CLEARANCE": self.DATE_OF_CLEARANCE,
            "HOUR_FROM": self.HOUR_FROM,
            "HOUR_TO": self.HOUR_TO,
            "ADDRESS_X": self.ADDRESS_X,
            "LONGITUDE_X": self.LONGITUDE_X,
            "LATITUDE_X": self.LATITUDE_X,
            "point": self.point,
            "year": self.year,
            "day": self.day,
            "month": self.month,
            "time": self.time,
            "hour": self.hour
        }


class IntervalFive(db.DynamicDocument):
    _id = db.ObjectIdField()
    INCIDENT_NO = db.StringField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    DAYOFWEEK = db.StringField()
    CPD_NEIGHBORHOOD = db.StringField()
    WEAPONS = db.StringField()
    DATE_OF_CLEARANCE = db.StringField()
    HOUR_FROM = db.IntField()
    HOUR_TO = db.IntField()
    ADDRESS_X = db.StringField()
    LONGITUDE_X = db.FloatField()
    LATITUDE_X = db.FloatField()
    VICTIM_AGE = db.StringField()
    VICTIM_RACE = db.StringField()
    point = db.PointField()
    year = db.StringField()
    day = db.StringField()
    month = db.StringField()
    time = db.StringField()
    hour = db.StringField()
    meta = {'collection': 'police_cinci_data_interval_all_five',
            'strict': False}

    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "DAYOFWEEK": self.DAYOFWEEK,
            "CPD_NEIGHBORHOOD": self.CPD_NEIGHBORHOOD,
            "WEAPONS": self.WEAPONS,
            "DATE_OF_CLEARANCE": self.DATE_OF_CLEARANCE,
            "HOUR_FROM": self.HOUR_FROM,
            "HOUR_TO": self.HOUR_TO,
            "ADDRESS_X": self.ADDRESS_X,
            "LONGITUDE_X": self.LONGITUDE_X,
            "LATITUDE_X": self.LATITUDE_X,
            "point": self.point,
            "year": self.year,
            "day": self.day,
            "month": self.month,
            "time": self.time,
            "hour": self.hour
        }


class IntervalSix(db.DynamicDocument):
    _id = db.ObjectIdField()
    INCIDENT_NO = db.StringField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    DAYOFWEEK = db.StringField()
    CPD_NEIGHBORHOOD = db.StringField()
    WEAPONS = db.StringField()
    DATE_OF_CLEARANCE = db.StringField()
    HOUR_FROM = db.IntField()
    HOUR_TO = db.IntField()
    ADDRESS_X = db.StringField()
    LONGITUDE_X = db.FloatField()
    LATITUDE_X = db.FloatField()
    VICTIM_AGE = db.StringField()
    VICTIM_RACE = db.StringField()
    point = db.PointField()
    year = db.StringField()
    day = db.StringField()
    month = db.StringField()
    time = db.StringField()
    hour = db.StringField()
    meta = {'collection': 'police_cinci_data_interval_all_six',
            'strict': False}

    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "DAYOFWEEK": self.DAYOFWEEK,
            "CPD_NEIGHBORHOOD": self.CPD_NEIGHBORHOOD,
            "WEAPONS": self.WEAPONS,
            "DATE_OF_CLEARANCE": self.DATE_OF_CLEARANCE,
            "HOUR_FROM": self.HOUR_FROM,
            "HOUR_TO": self.HOUR_TO,
            "ADDRESS_X": self.ADDRESS_X,
            "LONGITUDE_X": self.LONGITUDE_X,
            "LATITUDE_X": self.LATITUDE_X,
            "point": self.point,
            "year": self.year,
            "day": self.day,
            "month": self.month,
            "time": self.time,
            "hour": self.hour
        }
