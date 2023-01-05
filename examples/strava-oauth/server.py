# git subtree push --prefix examples/strava-oauth heroku main
# Strava tokens https://www.strava.com/settings/api
# Env vars https://devcenter.heroku.com/articles/config-vars
# https://dev.to/vulcanwm/environment-variables-in-heroku-python-385o
#!flask/bin/python
from datetime import datetime, timezone, timedelta
import logging
import re
import time

from flask import Flask, render_template, redirect, url_for, request, jsonify
import pickle
import json
# import sklearn as sklearn
import numpy as np
# Enviroment variables - https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1
import os
from dotenv import load_dotenv
from stravalib import Client
# Run FE and BE servers at once
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app) 

load_dotenv()

# STRAVA_CLIENT_ID=98820
# STRAVA_CLIENT_SECRET='e7ee484661cc7f1c9fd0e5974f137b8b9ec1314b'
# STRAVA_ACCESS_TOKEN='ac8c8989ce6c2ebb3bbedaa23e966a08e813f0f2'
STRAVA_REFRESH_TOKEN='1a266912e21a6c5ee7c248d5f9e674040b44c332'
STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET= os.getenv('STRAVA_CLIENT_SECRET')
# STRAVA_CLIENT_ID = os.environ.get('STRAVA_CLIENT_ID')
# STRAVA_CLIENT_SECRET= os.environ.get('STRAVA_CLIENT_SECRET')

# Global client object
client = Client()


@app.route("/")
def hello():
    return 'Hi there'

# @app.route("/")
# def login():
#     url = client.authorization_url(
#         client_id=STRAVA_CLIENT_ID,
#         redirect_uri=url_for('.logged_in', _external=True),
#         approval_prompt='auto')
#     return render_template('login.html', authorize_url=url)

# @app.route("/strava-oauth")
# def logged_in():
#     """
#     Method called by Strava (redirect) that includes parameters.
#     - state
#     - code
#     - error
#     """
#     error = request.args.get('error')
#     state = request.args.get('state')
#     if error:
#         return render_template('login_error.html', error=error)
#     else:
#         code = request.args.get('code')
#         token_response = client.exchange_code_for_token(
#             client_id=STRAVA_CLIENT_ID,
#             client_secret=STRAVA_CLIENT_SECRET,
#             code=code)
#         access_token = token_response['access_token']
#         expires_at = token_response['expires_at']

#         # Now store that short-lived access token somewhere (a database?)
#         client.access_token = access_token

#         # Probably here you'd want to store this somewhere -- e.g. in a database.
#         strava_athlete = client.get_athlete()
        
#         # If token expires
#         # if time.time() > expires_at:
#         #     refresh_response = client.refresh_access_token(
#         #         client_id=STRAVA_CLIENT_ID,
#         #         client_secret=STRAVA_CLIENT_SECRET,
#         #         refresh_token= STRAVA_REFRESH_TOKEN
#         #     )
#         #     access_token = refresh_response['access_token']
#         #     expires_at = refresh_response['expires_at']

#         # return render_template('login_results.html', athlete=strava_athlete, access_token=access_token)
#         # dashboard = 'http://localhost:3000/dashboard/app'
#         dashboard = 'https://elec49x.netlify.app/dashboard/app'
#         return redirect(dashboard)
        

# def load_models():
#     """"
#     Take the pickled model file, and open and load it into a variable called "model" 
#     Return: "model", an object of our model
#     """
#     file_name = "examples/strava-oauth/model_file.p"
#     with open(file_name, 'rb') as pickled:
#         data = pickle.load(pickled)
#         model = data['model']
#     return model  


# @app.route("/predict", methods=["POST"])
# def predict():
#     response = {}
    
#     types = ['time', 'latlng', 'distance', 'altitude', 'velocity_smooth', 
#     'heartrate', 'cadence', 'watts', 'temp', 'moving', 'grade_smooth']

#     # Get all activity
#     # https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities
#     # To get activities in oldest to newest, specify a value for the after argument. To get newest to oldest use before argument.
#     activity_response_array = []
#     heartrate_response_array = []
    
#     one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
#     one_week_ago = str(one_week_ago.strftime('%Y-%m-%dT%H:%M:%SZ'))

#     total_hour, total_min, total_sec, weekly_training_time = 0, 0, 0, 0

#     for activity in client.get_activities(after = one_week_ago, limit=10):
#         print("{0.moving_time}".format(activity))
#         activity_response_array.append("{0.name} {0.moving_time}".format(activity))
#         [hour, min, sec] = "{0.moving_time}".format(activity).split(":")
#         total_hour += int(hour)
#         total_min += int(min)
#         total_sec += int(sec)
#         weekly_training_time= str(timedelta(seconds=total_sec, minutes=total_min, hours=total_hour))
        
#         # Activities can have many streams, you can request n desired stream types
#         stream = client.get_activity_streams(activity.id, types=types, resolution='high')

#         # Result is a dictionary object.  The dict's key are the stream type.
#         total_bmp = 0
#         count = 0
#         if 'heartrate' in stream.keys():
#             for bpm in stream['heartrate'].data:
#                 total_bmp += bpm
#                 count += 1
#             print(stream['heartrate'].data)
#             heartrate_response_array.append(round(total_bmp/count))
    
#     response['heartrate_response'] = heartrate_response_array[-1] if heartrate_response_array else 0
#     response['activity_response'] = activity_response_array
#     response['weekly_training_time_response'] = weekly_training_time

#     model = load_models() # Get an instance of the model calling the load_models()
#     data = json.loads(request.data) # Load the request from the user and store in the variable "data"
#     hrv = data['hrv']

#     # Raises a 400 error if invalid input
#     if not hrv.isdigit():
#         return 'User entered invalid input type', 400

#     response['hrv'] = int(hrv)

#     # x_test = np.array([hrv]) # Create a X_test variable of the user's input
#     # recovery_score = model.predict(x_test.reshape(1, -1)) # Use the the  X_test to to predict the success using the  predict()
#     response['recovery_score'] = 23 # Dump the result to be sent back to the frontend
    
#     # response['recover_recommendation']

#     response = json.dumps(response)
#     print(response)

#     return json.dumps(response)

if __name__ == '__main__':
    app.run(debug=True)
