from flask import Flask, request, render_template, redirect, url_for, jsonify
import time
from shapely.geometry import box
from pyproj import Transformer
from geopy.exc import GeocoderTimedOut
import geopandas as gpd
import json
from key import key
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import os
from models import db
from models import Model
from griddata import gridcounts

#TO-DO Need to add a seperate endpoint that computes the grid for different sizes

load_dotenv()

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db': 'sample_geospatial',
    'host': os.getenv('MONGODB_URI'),
}
db.init_app(app)

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


def load_dataset():
    #remove_duplicates()

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

def compute_zscore():
    print("Starting function")

def coord_lister(geom):
    coords = list(geom.exterior.coords)
    return (coords)


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
        print("radians: ", radians)
    return radians

def get_meters(radius, unit):
    radius = int(radius)
    if unit == "meters":
        return radius
    elif unit == "miles":
        return radius * 1609.34
    else:
        return radius * 1000

def get_crimecounts_forlocation(coordinates, data, distance):
    Model.create_index([("point", "2dsphere")])

    #Return counts of documents
    count = Model.objects.all().count()
    print("count",count)

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
        #print("distance_near_list", len(distance_near_list))
        print("distance_near_list", distance_near_list)
    else:
        print("query does not return a result", distance_near_list)
    return len(distance_near_list)


GRID_DISTANCES_LIST = [
    (500, "meters"),
    (1, "miles"),
    (2, "miles"),
    (5, "miles")
]


def get_count_of_grid_new(polygon_dict):
    start_time = time.time()
    sublists = [polygon_dict[i:i + 5] for i in range(0, len(polygon_dict), 5)]
    count_list = [search_within_polygon(sublist) for sublist in sublists]
    #print("count_list", count_list)
    print("--- %s secconds ---" % (time.time() - start_time))
    return count_list


def search_within_polygon(sublistelement):

    # print("polygon1 type", type(polygon1))
    # print("sublistelement type", type(sublistelement))
    # print("sublistelement", sublistelement)

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
    result = Model.objects().aggregate(*polygon_pipeline)
    polygon_result_list = [doc for doc in result]
    if len(polygon_result_list) != 0:
        print("polygon_result_list", len(polygon_result_list))
    # else:
    #     print("query does not return a result", polygon_result_list)
    # print("--- %s secconds ---" % (time.time() - start_time))
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
                reversed_list.append(item[::-1])
                listcount += 1
        [reversed_list[listcount: (1 + listcount) * 5]]

    return reversed_list


def create_grid(cell_size_meters):
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


@app.route('/creategrids')
def create_grids():
    grid_cell_count = {}
    grid_geojson_parsed_list = []
    polygon_list = []

    for element in GRID_DISTANCES_LIST:
        distance = get_meters(element[0], element[1])
        grid = create_grid(distance)
        grid_geojson = grid.to_json()
        grid_geojson_parsed = json.loads(grid_geojson)
        polygon = reverse_coordinates(grid_geojson_parsed)
        # print("polygon",polygon)
        polygon_list.append(polygon)
        count_list = get_count_of_grid_new(polygon)
        print("count_list",count_list)

    return jsonify(polygon_list)




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
        meters = get_meters(user.radius, user.units)

        countsafe = get_crimecounts_forlocation(user.safecoordinates, filtered_data_list, meters)
        countwork = get_crimecounts_forlocation(user.workcoordinates, filtered_data_list, meters)
        countcurrent = get_crimecounts_forlocation(user.currentcoordinates, filtered_data_list, meters)
        print("countsafe", countsafe, "countwork", countwork, "countcurrent", countcurrent)
        #grid_geojson_parsed = grid_geojson_parsed_list[0]
        #griddata=json.dumps(grid_geojson_parsed)

        return render_template('success.html', key=key)
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
