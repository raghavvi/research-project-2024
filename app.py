from flask import Flask, request, render_template, redirect, url_for, jsonify
import time

from shapely.geometry import box
from pyproj import Transformer, Proj, transform
from geopy.exc import GeocoderTimedOut
import geopandas as gpd
import json
from key import key
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import os
from models import db, PolygonModel
from models import Model
from griddata import gridcounts
import numpy as np
import geopy.distance

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

def load_dataset2():
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
        print("getting new list", newlist)
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
    point_results = [result for result in data if result.get('point') != [0, 0]]

    heavy_crime_list = ['FELONIOUS ASSAULT', 'ASSAULT', 'AGGRAVATED BURGLARY',
                        'AGGRAVATED ROBBERY', 'RAPE', 'ROBBERY', 'MURDER']
    offense_result = [result for result in point_results if result.get('OFFENSE') in heavy_crime_list]
    filtered_results = filter_time_interval(interval, offense_result)

    return filtered_results


def switch_grids(grid):
    if grid == "700 meters":
        return gridcounts["700meters"]
    elif grid == "750 meters":
        return gridcounts["750meters"]
    elif grid == "800 meters":
        return gridcounts["800meters"]
    elif grid == "850 meters":
        return gridcounts["800meters"]
    if grid == "900 meters":
        return gridcounts["900meters"]
    elif grid == "950 meters":
        return gridcounts["950meters"]
    elif grid == "1 kilometer":
        return gridcounts["1kilometer"]
    elif grid == "1 mile":
        return gridcounts["1mile"]


@app.route('/data/<grid>/<safe>/<work>/<current>')
def compared_grid_counts(grid, safe, work, current):
    safe = int(safe)
    work = int(work)
    current = int(current)

    data = {}
    gridselected = switch_grids(grid)
    data['grid'] = gridselected
    data['safecount'] = safe
    data['workcount'] = work
    data['currentcount'] = current

    return jsonify(data)


@app.route('/data/<grid>/<safe>/<work>/<current>')
def compute_probabilities(grid, safe, work, current):
    safe = int(safe)
    work = int(work)
    current = int(current)

    data = {}

    griddistance = switch_grids(grid)

    # data = gridcounts["700meters:12AM-3AM"]

    gridcounts = sum(griddistance)
    gridcountarray = np.array(griddistance)
    # Test Exclude zeros from the data
    # nonzero_data = onemilecountarray[onemilecountarray != 0]

    gridcount_mean = np.mean(griddistance)
    max_gridcount = np.max(gridcountarray)
    min_grid_probability = 0
    safe_probability = safe / gridcounts
    work_probability = work / gridcounts
    current_probability = current / gridcounts
    max_grid_probability = max_gridcount / gridcounts

    # 0, mean, radius probability counts
    data["mingrid_probability"] = min_grid_probability
    data["safe_probability"] = safe_probability
    data["work_probability"] = work_probability
    data["current_probability"] = current_probability
    data["gridcount_mean"] = gridcount_mean
    data["max_grid_probability"] = max_grid_probability

    return jsonify(data)


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


GRID_DISTANCES_NEW_LIST = [
    # (700, "meters", "All"),
    (700, "meters", "12AM-3AM")
    #(700, "meters", "4AM-7AM")
    # (700, "meters", "8AM-11AM"),
    # (700, "meters", "12PM-3PM"),
    # (700, "meters", "4PM-7PM"),
    # (700, "meters", "8PM-11PM"),
    # (750, "meters", "12AM-3AM"),
    # (750, "meters", "4AM-7AM"),
    # (750, "meters", "8AM-11AM"),
    # (750, "meters", "12PM-3PM"),
    # (750, "meters", "4PM-7PM"),
    # (750, "meters", "8PM-11PM"),
    # (800, "meters", "12AM-3AM"),
    # (800, "meters", "4AM-7AM"),
    # (800, "meters", "8AM-11AM"),
    # (800, "meters", "12PM-3PM"),
    # (800, "meters", "4PM-7PM"),
    # (800, "meters", "8PM-11PM"),
    # (850, "meters", "12AM-3AM"),
    # (850, "meters", "4AM-7AM"),
    # (850, "meters", "8AM-11AM"),
    # (850, "meters", "12PM-3PM"),
    # (850, "meters", "4PM-7PM"),
    # (850, "meters", "8PM-11PM"),
    # (900, "meters", "12AM-3AM"),
    # (900, "meters", "4AM-7AM"),
    # (900, "meters", "8AM-11AM"),
    # (900, "meters", "12PM-3PM"),
    # (900, "meters", "4PM-7PM"),
    # (900, "meters", "8PM-11PM"),
    # (950, "meters", "12AM-3AM"),
    # (950, "meters", "4AM-7AM"),
    # (950, "meters", "8AM-11AM"),
    # (950, "meters", "12PM-3PM"),
    # (950, "meters", "4PM-7PM"),
    # (950, "meters", "8PM-11PM"),
    # (1, "kilometer", "12AM-3AM"),
    # (1, "kilometer", "4AM-7AM"),
    # (1, "kilometer", "8AM-11AM"),
    # (1, "kilometer", "12PM-3PM"),
    # (1, "kilometer", "4PM-7PM"),
    # (1, "kilometer", "8PM-11PM"),
    # (1, "mile", "12AM-3AM"),
    # (1, "mile", "4AM-7AM"),
    # (1, "mile", "8AM-11AM"),
    # (1, "mile", "12PM-3PM"),
    # (1, "mile", "4PM-7PM"),
    # (1, "mile", "8PM-11PM")
]

GRID_DISTANCES_LIST = [
    (700, "meters", "12AM-3AM")
]


def get_count_of_grid_new(polygon_dict, interval, data):
    start_time = time.time()
    sublists = [polygon_dict[i:i + 5] for i in range(0, len(polygon_dict), 5)]
    count_list = [search_within_polygon(sublist, interval, data) for sublist in sublists]
    # print("count_list", count_list)
    print("--- %s secconds ---" % (time.time() - start_time))
    return count_list


def search_within_polygon(sublistelement, interval, data):

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

    result = PolygonModel.objects.aggregate(*polygon_pipeline)
    polygon_result_list = [doc for doc in result]

    # if len(polygon_result_list) != 0:
        # print("new_data_list", polygon_result_list[0])
        # print("polygon_result_list", len(polygon_result_list))
    return len(polygon_result_list)


def select_interval_type(model, filtered_model, interval):
    if interval != "All":
        return filtered_model
    else:
        return model.objects().all()


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


@app.route('/createnewgrid')
def create_grids():
    polygon_list = []
    #Model add hour field aggregate to police_cinci_data_new
    # filter out where point = [0,0]
    # Filter out offense list
    #iterate through result list and save to new model
    # from the new model filter by the interval then apply the polygon_pipeline

    #need to avoid adding new records to save
    hour_aggregate_data = load_dataset2()
    for element in GRID_DISTANCES_LIST:
        distance = get_meters(element[0], element[1])
        print("distance", distance)
        grid = create_grid(distance)
        interval = element[2]
        data = filter_dataset(interval, hour_aggregate_data)
        filtered_data_list = [doc for doc in data]
        print('filtered_data_list', filtered_data_list[0:5])
        #test if data gets saved
        for doc in filtered_data_list:
            new_model_instance = PolygonModel(**doc)
            new_model_instance.save()

        grid_geojson = grid.to_json()
        grid_geojson_parsed = json.loads(grid_geojson)
        polygon = reverse_coordinates(grid_geojson_parsed)
        # print("polygon", polygon)
        polygon_list.append(polygon)
        count_list = get_count_of_grid_new(polygon, interval,data)
        print("element", element)
        print("count_list", count_list)

    return jsonify(polygon_list)


@app.route('/testgrids')
def test_grids():
    distance = get_meters(950, "meters")
    grid = create_grid(distance)
    grid_geojson = grid.to_json()
    grid_geojson_parsed = json.loads(grid_geojson)
    polygon = reverse_coordinates(grid_geojson_parsed)

    return render_template('gridmap.html', polygon=grid_geojson_parsed, key=key)


@app.route('/success/<safe>/<work>/<current>/<destination>/<interval>/<gridsize>')
def success(safe, work, current, destination, interval, gridsize):
    geolocator = Nominatim(user_agent="project-flask")
    try:
        safelocation = geolocator.geocode(safe)
        worklocation = geolocator.geocode(work)
        currentlocation = geolocator.geocode(current)
        destinationlocation = geolocator.geocode(destination)
        print("destinationlocation", destinationlocation)
        # Need to add destination to user class and add count function
        user = UserData()
        user.add_safe_coordinates(safelocation.latitude, safelocation.longitude)
        print(user.safecoordinates)

        user.add_work_coordinates(worklocation.latitude, worklocation.longitude)
        print(user.workcoordinates)

        user.add_current_coordinates(currentlocation.latitude, currentlocation.longitude)
        print(user.currentcoordinates)

        user.add_destination_coordinates(destinationlocation.latitude, destinationlocation.longitude)
        print(user.destinationcoordinates)

        gridsplit = gridsize.split()
        radius = gridsplit[0]
        unit = gridsplit[1]
        # print("radius",radius)
        # print("unit",unit)

        user.interval = interval
        user.radius = radius
        user.units = unit
        user.grid = gridsize

        aggregate_data = load_dataset()
        data = filter_dataset(user.interval, aggregate_data)
        filtered_data_list = [doc for doc in data]

        meters = get_meters(user.radius, user.units)

        countsafe = get_crimecounts_forlocation(user.safecoordinates, filtered_data_list, meters)
        countwork = get_crimecounts_forlocation(user.workcoordinates, filtered_data_list, meters)
        countcurrent = get_crimecounts_forlocation(user.currentcoordinates, filtered_data_list, meters)
        countdestination = get_crimecounts_forlocation(user.destinationcoordinates, filtered_data_list, meters)
        print("countsafe", countsafe, "countwork", countwork, "countcurrent", countcurrent, "countdestination",
              countdestination)

        # compared_grid_counts(user.grid, countsafe, countwork, countcurrent)
        compute_probabilities(user.grid, countsafe, countwork, countcurrent)

        return render_template('success.html', key=key, grid=user.grid, safe=countsafe, work=countwork,
                               current=countcurrent, destination=countdestination)
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
        # radius = request.form.get("radius")
        # unit = request.form.get("unit")
        gridsize = request.form.get("gridsize")

        return redirect(url_for('success', safe=safe, work=work, current=current, destination=destination,
                                interval=interval, gridsize=gridsize))

    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
