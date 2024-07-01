from flask_mongoengine import MongoEngine

db = MongoEngine()


# data should be filtered by frontend user. Need to validate
class Model(db.Document):
    id = db.ObjectIdField()
    INCIDENT_NO = db.IntField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    CLSD = db.StringField()
    UCR = db.IntField()
    DST = db.IntField()
    BEAT = db.IntField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    FLOOR = db.StringField()
    OPENING = db.StringField()
    SIDE = db.StringField()
    HATE_BIAS = db.StringField()
    DAYOFWEEK = db.StringField()
    RPT_AREA = db.IntField()
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
    meta = {'collection': 'police_cinci_data_new',
            'strict': False}

    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "CLSD": self.CLSD,
            "UCR": self.UCR,
            "DST": self.DST,
            "BEAT": self.BEAT,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "FLOOR": self.FLOOR,
            "OPENING": self.OPENING,
            "SIDE": self.SIDE,
            "HATE_BIAS": self.HATE_BIAS,
            "DAYOFWEEK": self.DAYOFWEEK,
            "RPT_AREA": self.RPT_AREA,
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
class PolygonModel(db.DynamicDocument):
    _id = db.ObjectIdField()
    INCIDENT_NO = db.IntField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    CLSD = db.StringField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    FLOOR = db.StringField()
    OPENING = db.StringField()
    SIDE = db.StringField()
    HATE_BIAS = db.StringField()
    DAYOFWEEK = db.StringField()
    RPT_AREA = db.IntField()
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
    meta = {'collection': 'police_cinci_data_polygon_new',
            'strict': False}

    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "CLSD": self.CLSD,
            "UCR": self.UCR,
            "DST": self.DST,
            "BEAT": self.BEAT,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "FLOOR": self.FLOOR,
            "OPENING": self.OPENING,
            "SIDE": self.SIDE,
            "HATE_BIAS": self.HATE_BIAS,
            "DAYOFWEEK": self.DAYOFWEEK,
            "RPT_AREA": self.RPT_AREA,
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
    INCIDENT_NO = db.IntField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    CLSD = db.StringField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    FLOOR = db.StringField()
    OPENING = db.StringField()
    SIDE = db.StringField()
    HATE_BIAS = db.StringField()
    DAYOFWEEK = db.StringField()
    RPT_AREA = db.IntField()
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
    meta = {'collection': 'police_cinci_data_interval_one',
            'strict': False}

    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "CLSD": self.CLSD,
            "UCR": self.UCR,
            "DST": self.DST,
            "BEAT": self.BEAT,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "FLOOR": self.FLOOR,
            "OPENING": self.OPENING,
            "SIDE": self.SIDE,
            "HATE_BIAS": self.HATE_BIAS,
            "DAYOFWEEK": self.DAYOFWEEK,
            "RPT_AREA": self.RPT_AREA,
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
    INCIDENT_NO = db.IntField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    CLSD = db.StringField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    FLOOR = db.StringField()
    OPENING = db.StringField()
    SIDE = db.StringField()
    HATE_BIAS = db.StringField()
    DAYOFWEEK = db.StringField()
    RPT_AREA = db.IntField()
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
    meta = {'collection': 'police_cinci_data_interval_two',
            'strict': False}

    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "CLSD": self.CLSD,
            "UCR": self.UCR,
            "DST": self.DST,
            "BEAT": self.BEAT,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "FLOOR": self.FLOOR,
            "OPENING": self.OPENING,
            "SIDE": self.SIDE,
            "HATE_BIAS": self.HATE_BIAS,
            "DAYOFWEEK": self.DAYOFWEEK,
            "RPT_AREA": self.RPT_AREA,
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
    INCIDENT_NO = db.IntField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    CLSD = db.StringField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    FLOOR = db.StringField()
    OPENING = db.StringField()
    SIDE = db.StringField()
    HATE_BIAS = db.StringField()
    DAYOFWEEK = db.StringField()
    RPT_AREA = db.IntField()
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
    meta = {'collection': 'police_cinci_data_interval_three',
            'strict': False}

    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "CLSD": self.CLSD,
            "UCR": self.UCR,
            "DST": self.DST,
            "BEAT": self.BEAT,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "FLOOR": self.FLOOR,
            "OPENING": self.OPENING,
            "SIDE": self.SIDE,
            "HATE_BIAS": self.HATE_BIAS,
            "DAYOFWEEK": self.DAYOFWEEK,
            "RPT_AREA": self.RPT_AREA,
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
    INCIDENT_NO = db.IntField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    CLSD = db.StringField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    FLOOR = db.StringField()
    OPENING = db.StringField()
    SIDE = db.StringField()
    HATE_BIAS = db.StringField()
    DAYOFWEEK = db.StringField()
    RPT_AREA = db.IntField()
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
    meta = {'collection': 'police_cinci_data_interval_four',
            'strict': False}

    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "CLSD": self.CLSD,
            "UCR": self.UCR,
            "DST": self.DST,
            "BEAT": self.BEAT,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "FLOOR": self.FLOOR,
            "OPENING": self.OPENING,
            "SIDE": self.SIDE,
            "HATE_BIAS": self.HATE_BIAS,
            "DAYOFWEEK": self.DAYOFWEEK,
            "RPT_AREA": self.RPT_AREA,
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
    INCIDENT_NO = db.IntField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    CLSD = db.StringField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    FLOOR = db.StringField()
    OPENING = db.StringField()
    SIDE = db.StringField()
    HATE_BIAS = db.StringField()
    DAYOFWEEK = db.StringField()
    RPT_AREA = db.IntField()
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
    meta = {'collection': 'police_cinci_data_interval_five',
            'strict': False}

    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "CLSD": self.CLSD,
            "UCR": self.UCR,
            "DST": self.DST,
            "BEAT": self.BEAT,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "FLOOR": self.FLOOR,
            "OPENING": self.OPENING,
            "SIDE": self.SIDE,
            "HATE_BIAS": self.HATE_BIAS,
            "DAYOFWEEK": self.DAYOFWEEK,
            "RPT_AREA": self.RPT_AREA,
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
    INCIDENT_NO = db.IntField()
    DATE_REPORTED = db.StringField()
    DATE_FROM = db.StringField()
    DATE_TO = db.StringField()
    CLSD = db.StringField()
    OFFENSE = db.StringField()
    LOCATION = db.StringField()
    THEFT_CODE = db.StringField()
    FLOOR = db.StringField()
    OPENING = db.StringField()
    SIDE = db.StringField()
    HATE_BIAS = db.StringField()
    DAYOFWEEK = db.StringField()
    RPT_AREA = db.IntField()
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
    meta = {'collection': 'police_cinci_data_interval_six',
            'strict': False}

    def to_json(self):
        return {
            "INCIDENT_NO": self.INCIDENT_NO,
            "DATE_REPORTED": self.DATE_REPORTED,
            "DATE_FROM": self.DATE_FROM,
            "DATE_TO": self.DATE_TO,
            "CLSD": self.CLSD,
            "UCR": self.UCR,
            "DST": self.DST,
            "BEAT": self.BEAT,
            "OFFENSE": self.OFFENSE,
            "LOCATION": self.LOCATION,
            "THEFT_CODE": self.THEFT_CODE,
            "FLOOR": self.FLOOR,
            "OPENING": self.OPENING,
            "SIDE": self.SIDE,
            "HATE_BIAS": self.HATE_BIAS,
            "DAYOFWEEK": self.DAYOFWEEK,
            "RPT_AREA": self.RPT_AREA,
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