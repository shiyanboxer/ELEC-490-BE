# Strava tokens https://www.strava.com/settings/api

#!flask/bin/python
import logging

from flask import Flask, render_template, redirect, url_for, request, jsonify
import pickle
import json
# import sklearn as sklearn
import numpy as np
# Enviroment variables - https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1
import os
from dotenv import load_dotenv
from stravalib import Client

app = Flask(__name__)

load_dotenv()

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET= os.getenv('STRAVA_CLIENT_SECRET')

@app.route("/")
def login():
    client = Client()

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
        client = Client()
        access_token = client.exchange_code_for_token(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            code=code)
        
        # Probably here you'd want to store this somewhere -- e.g. in a database.
        strava_athlete = client.get_athlete()
        
        return render_template('login_results.html', athlete=strava_athlete, access_token=access_token)


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


@app.route("/predict")
def predict():
    client = Client()
    
    types = ['time', 'latlng', 'distance', 'altitude', 'velocity_smooth', 
    'heartrate', 'cadence', 'watts', 'temp', 'moving', 'grade_smooth']

    # Get all activity
    # https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities
    # To get activities in oldest to newest, specify a value for the after argument. To get newest to oldest use before argument.
    for activity in client.get_activities(after = "2010-01-01T00:00:00Z",  limit=10):
        print("{0.name} {0.moving_time}".format(activity))
        
        # Activities can have many streams, you can request n desired stream types
        stream = client.get_activity_streams(activity.id, types=types, resolution='high')

        # Result is a dictionary object.  The dict's key are the stream type.
        if 'heartrate' in stream.keys():
            print(stream['heartrate'].data)
    
    
    model = load_models() # Get an instance of the model calling the load_models()
    data = json.loads(request.data) # Load the request from the user and store in the variable "data"

    # Raises a 400 error if invalid input
    if type(data['hrv_value']) != int:
        return 'User entered invalid input type', 400

    hrv_value = float(data['hrv_value']) # Break down each input into seprate variables 
    
    x_test = np.array([hrv_value]) # Create a X_test variable of the user's input
    prediction = model.predict(x_test.reshape(1, -1)) # Use the the  X_test to to predict the success using the  predict()
    response = json.dumps({'response': np.around(prediction[0], 0)}) # Dump the result to be sent back to the frontend
    
    return response

if __name__ == '__main__':
    app.run(debug=True)
