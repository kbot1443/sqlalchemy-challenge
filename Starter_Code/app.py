# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy import desc, select as sel

# Database Setup

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


# Flask Setup

app = Flask(__name__)



# Flask Routes


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/enter start date in yyyy-mm-dd format <start><br/>"
        f"/api/v1.0/enter start and end date in yyyy-mm-dd/yyy-mm-dd"
       
    )
@app.route("/api/v1.0/precipitation")
def data():
    
    session = Session(engine)
    one_year_ago = "2016-08-23"

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()
    all_data = []
    for date, prcp in results:
        Measurement_dict = {}
        Measurement_dict["date"] = date
        Measurement_dict["prcp"] = prcp
        all_data.append(Measurement_dict)
    
    return jsonify(all_data)
    
@app.route("/api/v1.0/stations")
def stasion():
    session = Session(engine)
    result = session.query(Station.station).all()

    session.close()
    station_names = [row.station for row in result]

    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tob():
    one_year_ago = "2016-08-23"

    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= one_year_ago).\
    order_by(Measurement.date).all()
    session.close()
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {"date": date, "tobs": tobs}
        tobs_data.append(tobs_dict)
    
    return jsonify(tobs_data)
    
    
@app.route("/api/v1.0/<start>")
def enter_start_date(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    if results:
        min_tobs, max_tobs, avg_tobs = results[0]
        response = {
           "start_date": start,
           "min_tobs": min_tobs,
           "max_tobs": max_tobs,
           "avg_tobs": avg_tobs
        }

        return jsonify(response)

    return jsonify({"error": f"Cannot find any data for the date {start}"}), 404


@app.route("/api/v1.0/<start>/<end>")
def enter_start_end_date(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()
        

    if results:
        min_tobs, max_tobs, avg_tobs = results[0]
        response = {
            "start_date": start,
            "end_date": end,
            "min_tobs": min_tobs,
            "max_tobs": max_tobs,
            "avg_tobs": avg_tobs
        }

        return jsonify(response)

    return jsonify({"error": f"Cannot find any data between {start} and {end}"}), 404

if __name__ == '__main__':
    app.run(debug=True)