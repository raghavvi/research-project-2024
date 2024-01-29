import geojson
import shapely
import geopandas as gpd
from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_mongoengine import MongoEngine
from geopy import distance, Location
from geopy.exc import GeocoderTimedOut
from shapely.geometry import box
import json
from key import key
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import os
from pyproj import Proj, transform, Transformer

load_dotenv()

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db': 'sample_geospatial',
    'host': os.getenv('MONGODB_URI'),
}
db = MongoEngine(app)


class UserData:
    latitude = None
    longitude = None
    interval = None
    radius = 0
    units = None

    def __init__(self):
        self.safecoordinates = []
        self.workcoordinates = []
        self.currentcoordinates = []

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
    meta = {'collection': 'police_cinci_data',
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


class FilteredModel(db.Document):
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
    meta = {'strict': False}

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


def filter_time_interval(interval, data):
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
    return newlist


def filter_dataset(interval, data):
    # #Filter out crime incidents that do not have a location
    point_results = [result for result in data if result.get('point') != [0, 0]]

    heavy_crime_list = ['FELONIOUS ASSAULT', 'ASSAULT', 'AGGRAVATED BURGLARY',
                        'AGGRAVATED ROBBERY', 'RAPE', 'ROBBERY', 'MURDER']
    offense_result = [result for result in point_results if result.get('OFFENSE') in heavy_crime_list]
    filtered_results = filter_time_interval(interval, offense_result)

    return filtered_results


def reverse_coordinates(geojson):
    polygon_dict = {}
    reversed_list = []
    print("geojson", type(geojson))
    feature = geojson['features']
    geometry = feature[0]['geometry']
    coordinates = geometry['coordinates']
    print("geojson", coordinates)
    for inner_list in coordinates:
        for item in inner_list:
            print("item", item[::-1])
            reversed_list.append(item[::-1])
    polygon_dict["1"] = reversed_list

    print("polygon_dict", polygon_dict)
    return polygon_dict

def get_count_of_grid(polygon):
    count = 0
    polygon = {
        "type": "Polygon",
        "coordinates": [polygon.get("1")]
    }

    print("polygon",polygon)

    pointsfoundwithinpolygon = FilteredModel.objects(point__geo_within=polygon)
    print("pointsfoundwithinpolygon",pointsfoundwithinpolygon)

    if pointsfoundwithinpolygon:
        print("point found within polygon")
        count += 1
    else:
        print("point not found within polygon")

def coord_lister(geom):
    coords = list(geom.exterior.coords)
    return (coords)


def create_grid():
    cell_size_meters = 2500
    bbox = [-84.8192049318631, 39.0533271607855, -84.2545822217415, 39.3599982625544]

    minx = bbox[1]
    maxx = bbox[3]
    miny = bbox[0]
    maxy = bbox[2]

    transformer_4326_to_3857 = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
    transformer_3857_to_4326 = Transformer.from_crs("epsg:3857", "epsg:4326", always_xy=True)

    # Convert the bounding box to Web Mercator (EPSG:3857) to get a more accurate estimate of meters per degree
    minx, miny = transformer_4326_to_3857.transform(minx, miny)
    maxx, maxy = transformer_4326_to_3857.transform(maxx, maxy)

    # Calculate the number of cells in each dimension
    num_cells_x = int((maxx - minx) / cell_size_meters)
    num_cells_y = int((maxy - miny) / cell_size_meters)

    # Create a grid of rectangular cells
    grid_cells = []
    for i in range(num_cells_x):
        for j in range(num_cells_y):
            cell_minx = minx + i * cell_size_meters
            cell_miny = miny + j * cell_size_meters
            cell_maxx = minx + (i + 1) * cell_size_meters
            cell_maxy = miny + (j + 1) * cell_size_meters

            # Convert the cell bounding box back to WGS 84
            cell_minx, cell_miny = transformer_3857_to_4326.transform(cell_minx, cell_miny)
            cell_maxx, cell_maxy = transformer_3857_to_4326.transform(cell_maxx, cell_maxy)

            grid_cells.append(box(cell_minx, cell_miny, cell_maxx, cell_maxy))

    print("new grid_cells", grid_cells[0])

    # Create a GeoDataFrame from the grid cells
    grid_gdf = gpd.GeoDataFrame(geometry=grid_cells, crs="EPSG:4326")

    return grid_gdf


def compute_grid(mdistance):
    # get the min and max latitude, longitude of the datapoints
    bbox = [-84.8192049318631, 39.0533271607855, -84.2545822217415, 39.3599982625544]

    x = bbox[1]
    xf = bbox[3]
    y = bbox[0]
    yf = bbox[2]

    x0, y0 = (x, y)

    grid_cells = []
    while y0 <= yf:
        while x0 <= xf:
            grid_cells.append(shapely.geometry.box(x0, y0, x0 + mdistance, y0 + mdistance))
            x0 = x0 + mdistance
        x0 = x
        y0 = y0 + mdistance

    print("grid_cells", grid_cells[0])
    print("radians", mdistance)

    id = [i for i in range(len(grid_cells))]
    gridDf = gpd.GeoDataFrame({"id": id, "geometry": grid_cells})
    gridDf.crs = "EPSG:4326"

    geometry = gridDf["geometry"]

    polygon = geometry.apply(coord_lister)

    coordinates = [[list(y) for y in x] for x in polygon]

    print("coordinates0", coordinates[0])

    data = {
        'coordinates': coordinates
    }

    return data


def get_crimecounts_forlocation(coordinates, data, distance):
    Model.create_index([("point", "2dsphere")])

    longitude = coordinates[0]
    latitude = coordinates[1]

    # Extract points from filtered dataset
    # save filtered dataset to model
    model = [FilteredModel(INCIDENT_NO=item['INCIDENT_NO'], point=item['point'],
                           ADDRESS_X=item['ADDRESS_X'], OFFENSE=item['OFFENSE']) for item in data]

    FilteredModel.objects.insert(model)

    # model = return_data_duplicates(FilteredModel)
    # print("newmodelobjects",model.objects.all())

    newmodelobjects = FilteredModel.objects.all()
    # print("newmodelobjects", newmodelobjects)

    incidentnorecordset = set(record.INCIDENT_NO for record in newmodelobjects)

    count = 0
    for r in incidentnorecordset:
        # get the first record that matches with the incident no. Avoids duplicate records
        firstdocumentmatch = FilteredModel.objects(INCIDENT_NO=r).first()
        print("firstDocumentMatch", firstdocumentmatch['ADDRESS_X'], firstdocumentmatch['point'])
        # pointsfoundwithinradius = FilteredModel.objects(point=firstdocumentmatch['point'],
        #                                                 point__geo_within_sphere=[(longitude, latitude), 0.001])
        # vr
        # available_results = [[result.point,result.ADDRESS_X]for result in pointsfoundwithinradius]
        #
        # print("pointsfoundwithinradius",available_results[0],available_results[1])
        pointsfoundwithinradius = FilteredModel.objects(INCIDENT_NO=r,
                                                        point__geo_within_sphere=[(longitude, latitude),
                                                                                  distance])
        available_points = pointsfoundwithinradius.first()

        if pointsfoundwithinradius:
            print("point found within radius")
            print("pointsfoundwithinradius", available_points['ADDRESS_X'], available_points['point'])
            count += 1
        else:
            print("point not found within radius")

    # filteredrecordset = set(record for record in newmodelobjects)
    # print("get all reccords")
    # results = []
    # for m in newmodelobjects:
    #     print(f"ADDRESS_X: {m.ADDRESS_X}",f"point: {m.point}")
    #     pointsfoundwithinradius = FilteredModel.objects(point=m.point,point__geo_within_sphere=[center_point, radius/earth_radius])
    #     if pointsfoundwithinradius:
    #         results.append(pointsfoundwithinradius)
    #     else:
    #         print("No points found")
    return count


def get_radius(radius, unit):
    radius = float(radius)
    try:
        if unit == "meters":
            earthradius = 6378.1
            # convert meters to kilometers
            radius = radius / 1000
        elif unit == "miles":
            earthradius = 3963.2
        else:
            earthradius = 6378.1
    except Exception as e:
        print("Error: ", e)
    finally:
        radians = radius / earthradius

    return radians


@app.route('/success/<safe>/<work>/<current>/<interval>/<radius>/<unit>')
def success(safe, work, current, interval, radius, unit):
    geolocator = Nominatim(user_agent="project-flask")

    try:
        safelocation = geolocator.geocode(safe)
        worklocation = geolocator.geocode(work)
        currentlocation = geolocator.geocode(current)
        user = UserData()
        user.add_safe_coordinates(safelocation.latitude, safelocation.longitude)
        print(user.safecoordinates)

        user.add_work_coordinates(worklocation.latitude, worklocation.longitude)
        print(user.workcoordinates)

        user.add_current_coordinates(currentlocation.latitude, currentlocation.longitude)
        print(user.currentcoordinates)

        user.interval = interval
        user.radius = radius
        user.units = unit

        aggregate_data = load_dataset()
        data = filter_dataset(user.interval, aggregate_data)
        filtered_data_list = [doc for doc in data]

        radians = get_radius(user.radius, user.units)
        print("radians", radians)
        countsafe = get_crimecounts_forlocation(user.safecoordinates, filtered_data_list, radians)
        countwork = get_crimecounts_forlocation(user.workcoordinates, filtered_data_list, radians)
        countcurrent = get_crimecounts_forlocation(user.currentcoordinates, filtered_data_list, radians)

        print("countsafe", countsafe, "countwork", countwork, "countcurrent", countcurrent)

        grid_gdf = create_grid()
        grid_geojson = grid_gdf.to_json()

        grid_geojson_parsed = json.loads(grid_geojson)

        polygon = reverse_coordinates(grid_geojson_parsed)

        get_count_of_grid(polygon)

        return render_template('success.html', key=key, griddata=json.dumps(grid_geojson_parsed))
    except GeocoderTimedOut as e:
        return render_template('404.html'), 404


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        safe = request.form.get("safe")
        work = request.form.get("work")
        current = request.form.get("current")
        interval = request.form.get("interval")
        radius = request.form.get("radius")
        unit = request.form.get("unit")

        return redirect(url_for('success', safe=safe, work=work, current=current,
                                interval=interval, radius=radius, unit=unit))

    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
