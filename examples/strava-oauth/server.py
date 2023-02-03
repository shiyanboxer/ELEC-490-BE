# Issues with deployment to Heroku - change Authorization Callback Domain in Strava API settings
# https://www.reddit.com/r/Strava/comments/k1ka4w/strava_api_redirect_uri_and_callbackurlscheme/
# https://groups.google.com/g/strava-api/c/4NvcU1iaV6w
# git subtree push --prefix examples/strava-oauth heroku main
# Strava tokens https://www.strava.com/settings/api
# Env vars https://devcenter.heroku.com/articles/config-vars
# https://dev.to/vulcanwm/environment-variables-in-heroku-python-385o
#!flask/bin/python

from datetime import datetime, timezone, timedelta
import logging
import re
import time
import collections
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
# import pymongo
import bson.json_util
# import connection as connection

app = Flask(__name__)
cors = CORS(app) 

load_dotenv()

STRAVA_REFRESH_TOKEN=os.getenv('STRAVA_REFRESH_TOKEN')
STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET= os.getenv('STRAVA_CLIENT_SECRET')

# Global client object
client = Client()

# Session cookies
session = collections.defaultdict()

# Connect to database
# db = connection.connect_db()

# Default user
# CURRENT_USER = {
#     '_id': '63dbe6a0ac0494f8e62166f6',
#     'first_name': 'Shiyan',
#     'last_name': 'Boxer',
#     # 'recommendation': [{'date': datetime.date(2022, 9, 11, 20, 14, 14, 796000), 'recommendation_txt': 'workout more'}],
#     # 'recovery': [{'date': datetime.date(2022, 9, 11, 20, 14, 14, 796000), 'recovery_score': 40, 'hrv': 30}]
# }

@app.route("/")
def login():
    url = client.authorization_url(
        client_id=STRAVA_CLIENT_ID,
        redirect_uri=url_for('.logged_in', _external=True),
        approval_prompt='auto')
    return render_template('login.html', authorize_url=url)

@app.route("/strava-oauth")
def logged_in():
    error = request.args.get('error')
    state = request.args.get('state')
    if error:
        return render_template('login_error.html', error=error)
    else:
        code = request.args.get('code')
        token_response = client.exchange_code_for_token(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            code=code)
        access_token = token_response['access_token']
        expires_at = token_response['expires_at']

        # Now store that short-lived access token somewhere (a database?)
        client.access_token = access_token
        # Store the access token in a session cookie
        session['access_token'] = access_token
        session['expires_at'] = expires_at

        # Probably here you'd want to store this somewhere -- e.g. in a database.
        strava_athlete = client.get_athlete()
        session['first_name'] = strava_athlete.firstname
        session['last_name'] = strava_athlete.lastname
        
        # If token expires
        if time.time() > expires_at:
            refresh_response = client.refresh_access_token(
                client_id=STRAVA_CLIENT_ID,
                client_secret=STRAVA_CLIENT_SECRET,
                refresh_token= STRAVA_REFRESH_TOKEN
            )
            access_token = refresh_response['access_token']
            expires_at = refresh_response['expires_at']

        # return render_template('login_results.html', athlete=strava_athlete, access_token=access_token)
        # dashboard = 'http://localhost:3000/dashboard/app'
        dashboard = 'https://elec49x.netlify.app/dashboard/app'
        return redirect(dashboard)

# # @app.route("/user")
# # def get_user():
# #     find_by_name = { 
# #         "first_name": session.get('first_name', 'Fake'), 
# #         "last_name": session.get('last_name', 'Name')
# #     }
# #     users = db.find(find_by_name)

# #     for user in users:
# #         print(user)
# #     return json.loads(bson.json_util.dumps(user))

# # def load_models():
# #     """"
# #     Take the pickled model file, and open and load it into a variable called "model" 
# #     Return: "model", an object of our model
# #     """
# #     file_name = "examples/strava-oauth/model_file.p"
# #     with open(file_name, 'rb') as pickled:
# #         data = pickle.load(pickled)
# #         model = data['model']
# #     return model  


@app.route("/predict", methods=["POST"])
def predict():    
    # Retrieve the access token from the session cookie
    access_token = session.get('access_token')
    if access_token is None:
        return 'Access token not found', 400

    # Set the access token on the client object
    client.access_token = access_token

    response = {}
    
    types = ['time', 'latlng', 'distance', 'altitude', 'velocity_smooth', 
    'heartrate', 'cadence', 'watts', 'temp', 'moving', 'grade_smooth']

    # Get all activity
    # https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities
    # To get activities in oldest to newest, specify a value for the after argument. To get newest to oldest use before argument.
    activity_response_array = []
    heartrate_response_array = []
    
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    one_week_ago = str(one_week_ago.strftime('%Y-%m-%dT%H:%M:%SZ'))
    total_hour, total_min, total_sec, weekly_training_time = 0, 0, 0, 0

    for activity in client.get_activities(after = one_week_ago, limit=10):
        activity_response_array.append("{0.name} {0.moving_time}".format(activity))
        [hour, min, sec] = "{0.moving_time}".format(activity).split(":")
        total_hour += int(hour)
        total_min += int(min)
        total_sec += int(sec)
        weekly_training_time = round(total_hour + (total_min / 60) + (total_sec / 3600))
        
        # Activities can have many streams, you can request n desired stream types
        stream = client.get_activity_streams(activity.id, types=types, resolution='high')

        # Result is a dictionary object.  The dict's key are the stream type.
        total_bmp = 0
        count = 0
        if 'heartrate' in stream.keys():
            for bpm in stream['heartrate'].data:
                total_bmp += bpm
                count += 1
            # print(stream['heartrate'].data)
            heartrate_response_array.append(round(total_bmp/count))
    
    response['heartrate_response'] = heartrate_response_array[-1] if heartrate_response_array else 0
    response['activity_response'] = activity_response_array
    response['weekly_training_time_response'] = weekly_training_time

    # model = load_models() # Get an instance of the model calling the load_models()
    data = json.loads(request.data) # Load the request from the user and store in the variable "data"
    hrv = data['hrv']
    response['hrv'] = int(hrv)

    # x_test = np.array([hrv]) # Create a X_test variable of the user's input
    # recovery_score = model.predict(x_test.reshape(1, -1)) # Use the the  X_test to to predict the success using the  predict()
    response['recovery_score'] = 23 # Dump the result to be sent back to the frontend
    
    # response['recover_recommendation']

    response = json.dumps(response)
    print(response)

    return json.dumps(response)

if __name__ == '__main__':
    app.run(debug=True)
