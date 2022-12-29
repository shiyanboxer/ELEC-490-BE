# Strava tokens https://www.strava.com/settings/api

#!flask/bin/python
import logging
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

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET= os.getenv('STRAVA_CLIENT_SECRET')

# Global client object
client = Client()

@app.route("/")
def login():
    url = client.authorization_url(
        client_id=STRAVA_CLIENT_ID,
        redirect_uri=url_for('.logged_in',
        _external=True),
        approval_prompt='auto')
    return render_template('login.html', authorize_url=url)


@app.route("/strava-oauth")
def logged_in():
    """
    Method called by Strava (redirect) that includes parameters.
    - state
    - code
    - error
    """
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
        refresh_token = token_response['refresh_token']
        expires_at = token_response['expires_at']

        # Now store that short-lived access token somewhere (a database?)
        client.access_token = access_token

        # You must also store the refresh token to be used later on to obtain another valid access token
        # in case the current is already expired
        # client.refresh_token = refresh_token

        # Probably here you'd want to store this somewhere -- e.g. in a database.
        strava_athlete = client.get_athlete()
        
        # If token expires
        # if time.time() > client.expires_at:
        #     refresh_response = client.refresh_access_token(client_id=1234, client_secret='asdf1234',
        #         refresh_token=client.refresh_token)
        #     access_token = refresh_response['access_token']
        #     refresh_token = refresh_response['refresh_token']
        #     expires_at = refresh_response['expires_at']

        # return render_template('login_results.html', athlete=strava_athlete, access_token=access_token)
        # dashboard = 'https://elec49x.netlify.app/dashboard/app'
        dashboard = 'http://localhost:3000/dashboard/app'
        return redirect(dashboard)
        

def load_models():
    """"
    Take the pickled model file, and open and load it into a variable called "model" 
    Return: "model", an object of our model
    """
    file_name = "examples/strava-oauth/model_file.p"
    with open(file_name, 'rb') as pickled:
        data = pickle.load(pickled)
        model = data['model']
    return model  


@app.route("/predict", methods=["POST"])
def predict():
    types = ['time', 'latlng', 'distance', 'altitude', 'velocity_smooth', 
    'heartrate', 'cadence', 'watts', 'temp', 'moving', 'grade_smooth']

    # Get all activity
    # https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities
    # To get activities in oldest to newest, specify a value for the after argument. To get newest to oldest use before argument.
    activity_response = []
    heartrate_response = []

    for activity in client.get_activities(after = "2010-01-01T00:00:00Z",  limit=10):
        print("{0.name} {0.moving_time}".format(activity))
        activity_response.append("{0.name} {0.moving_time}".format(activity))
        
        # Activities can have many streams, you can request n desired stream types
        stream = client.get_activity_streams(activity.id, types=types, resolution='high')

        # Result is a dictionary object.  The dict's key are the stream type.
        if 'heartrate' in stream.keys():
            print(stream['heartrate'].data)
            heartrate_response.append(stream['heartrate'].data)
            
    model = load_models() # Get an instance of the model calling the load_models()
    data = json.loads(request.data) # Load the request from the user and store in the variable "data"
    hrv = int(data['hrv'])

    # Raises a 400 error if invalid input
    # if type(data['hrv']) != int:
    #     return 'User entered invalid input type', 400

    # x_test = np.array([hrv]) # Create a X_test variable of the user's input
    # prediction = model.predict(x_test.reshape(1, -1)) # Use the the  X_test to to predict the success using the  predict()
    # prediction_response = json.dumps({'prediction_response': np.around(prediction[0], 0)}) # Dump the result to be sent back to the frontend
    
    # TODO: concatenate all response and return
    # return response
    return json.dumps(hrv)

if __name__ == '__main__':
    app.run(debug=True)
