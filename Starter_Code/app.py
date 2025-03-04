# Import the dependencies.
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the SQL-Alchemy APP API for Hawaii Precipitation Data!<br/>"
        f"Here Are Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Precipitation Data"""
    # Query all Stations Precipitation
    sel = [measurement.date, 
        func.sum(measurement.prcp)]
    precipitation = session.query(*sel).\
            filter(measurement.date >= '2016-08-23').\
            group_by(measurement.date).\
            order_by(measurement.date).all()

    session.close()
    
    # Convert the list to Dictionary and JSONify
    precip_dates = []
    precip_totals = []

    for date, dailytotal in precipitation:
        precip_dates.append(date)
        precip_totals.append(dailytotal)
    
    precip_dict = dict(zip(precip_dates, precip_totals))

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Stations in Hawaii"""
    # Query all Stations in Hawaii
    sel = [measurement.station]
    active_stations = session.query(*sel).group_by(measurement.station).all()

    session.close()

    # Convert tuples to normal list and JSONify
    all_stations = list(np.ravel(active_stations))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all TOBs"""
    # Query all tobs
    sel = [measurement.date, 
        measurement.tobs]
    station_temps = session.query(*sel).\
            filter(measurement.date >= '2016-08-23', measurement.station == 'USC00519281').\
            group_by(measurement.date).\
            order_by(measurement.date).all()

    session.close()

    # Convert the list to Dictionary
    obs_dates = []
    temp_obs = []

    for date, observation in station_temps:
        obs_dates.append(date)
        temp_obs.append(observation)
    
    active_tobs = dict(zip(obs_dates, temp_obs))

    return jsonify(active_tobs)

    
@app.route("/api/v1.0/<start_date>")
def Start_date(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of min, avg and max tobs for a start date"""
    # Query all tobs
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start_date).all()

    session.close()
    # Check if results are empty
    if not results or results[0][0] is None:
        return jsonify({"error": "No data found for the provided start date."}), 404

    # Create a dictionary from the row data
    start_tobs = []
    for min_temp, avg_temp, max_temp in results:
        start_tobs_dict = {}
        start_tobs_dict["min_temp"] = min_temp
        start_tobs_dict["avg_temp"] = avg_temp
        start_tobs_dict["max_temp"] = max_temp
        start_tobs.append(start_tobs_dict) 
    return jsonify(start_tobs)

@app.route("/api/v1.0/<start_date>/<end_date>")
def Start_end_date(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of min, avg and max tobs for start and end dates"""
    # Query all tobs
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start_date).all()

    session.close()
    #Check is results are empty
    if not results:
        return jsonify({"error": "No data found for the provided date range."}), 404

    # Create a dictionary from the row data and append 
    start_end_tobs = []
    for min_temp, avg_temp, max_temp in results:
        start_end_tobs_dict = {}
        start_end_tobs_dict["min_temp"] = min_temp
        start_end_tobs_dict["avg_temp"] = avg_temp
        start_end_tobs_dict["max_temp"] = max_temp
        start_end_tobs.append(start_end_tobs_dict) 
    

    return jsonify(start_end_tobs)

if __name__ == "__main__":
    app.run(debug=True)