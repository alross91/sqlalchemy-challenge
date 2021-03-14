import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from datetime import timedelta
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
    """Available API Routes for Surfs Up"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Last Year of Precipitation Data"""
    session = Session(engine)
   # Find the most recent date in the data set.
    recentdate = session.query(measurement.date).order_by(measurement.date.desc()).first()


    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= '2016-08-23').all()
    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    """List of Weather Stations"""
    session = Session(engine)

    # select station names from stations table
    totalstations = session.query(func.count(station.station)).all()

    # Return JSONIFY List of Stations
    
    return jsonify(totalstations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Temperature Observations for Most Active Station for 2016 to 2017"""
    
   # Design a query to find the most active stations (i.e. what stations have the most rows?)
# List the stations and the counts in descending order.
    mostactive = session.query(measurement.station, func.count(measurement.station)).\
                  order_by(func.count(measurement.station).desc()).\
                  group_by(measurement.station).\
                  all()

# Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
#most active station
mostactive_station = mostactive[0][0]

#lowest temp recorded at the most active station
lowest_temp = session.query(func.min(measurement.tobs)).\
    filter(measurement.station == mostactive_station).scalar()
              

#highest temp recorded at the most active station
highest_temp = session.query(func.max(measurement.tobs)).\
    filter(measurement.station == mostactive_station).scalar()

# average temp recorded at the most active station
avg_temp = session.query(func.avg(measurement.tobs)).\
              filter(measurement.station == mostactive_station).scalar()


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    session = Session(engine)

    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        mostactive_temp = session.query(measurement.tobs).\
        .filter(measurement.date>='2016-08-23').\
        filter(measurement.station == mostactive[0][0]).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
  
    return jsonify(results)

if __name__ == '__main__':
    app.run()

