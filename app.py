import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station =Base.classes.station

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
        f"<p>Welcome to the Hawaii weather API!</p>"
        f"<p>Usage:</p>"
        f"/api/v1.0/precipitation<br/>Returns a JSON list of percipitation data for the dates between 8/23/16 and 8/23/17<br/><br/>"
        f"/api/v1.0/stations<br/>Returns a JSON list of the weather stations<br/><br/>"
        f"/api/v1.0/tobs<br/>Returns a JSON list of the Temperature Observations (tobs) for each station for the dates between 8/23/16 and 8/23/17<br/><br/>"
        f"/api/v1.0/date<br/>Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates between the given start date and 8/23/17<br/><br/>."
        f"/api/v1.0/start_date/end_date<br/>Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates between the given start date and end date<br/><br/>."
    )


# /api/v1.0/precipitation
# Convert the query results to a Dictionary using date as the key and tobs as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    results=session.query(*sel).\
    order_by(Measurement.date).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_precipitation.append(precipitation_dict)
    return jsonify(all_precipitation)


#/api/v1.0/stations
#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    active = session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()
    session.close()
    all_names = list(np.ravel(active))
    return jsonify(all_names)


#/api/v1.0/tobs
#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    active = session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()
    most_active=active[0][0]
    results=session.query(Measurement.date,Measurement.tobs).filter(Measurement.station==most_active).all()
    session.close()
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        all_tobs.append(tobs_dict)
    return jsonify(all_tobs)
    session.close()


#/api/v1.0/<start>
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def startdate(start):
    session = Session(engine)
    temp = [func.min(Measurement.tobs),
       func.max(Measurement.tobs),
       func.avg(Measurement.tobs)]
    start_date=session.query(Measurement.date).filter(Measurement.date == start)
    if start_date[0][0]==start:
        results=session.query(*temp).filter(Measurement.date > start).all()
        result=[f"Min TEMP = {results[0][0]}",f"MAX TEMP = {results[0][1]}",f"AVG TEMP = {results[0][2]}"]
        temp_ans=list(np.ravel(result))
        return jsonify(temp_ans)
    # else:
    #     return jsonify({"error": f"Date chosen {start} does not exist in database"}), 404



# /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    session = Session(engine)
    temp = [func.min(Measurement.tobs),
       func.max(Measurement.tobs),
       func.avg(Measurement.tobs)]
    start_date=session.query(Measurement.date).filter(Measurement.date == start).filter(Measurement.date ==end)
    results=session.query(*temp).filter(Measurement.date > start).filter(Measurement.date < end).all()
    result=[f"Min TEMP = {results[0][0]}",f"MAX TEMP = {results[0][1]}",f"AVG TEMP = {results[0][2]}"]
    temp_ans=list(np.ravel(result))
    return jsonify(temp_ans)


if __name__ == '__main__':
    app.run(debug=True)
