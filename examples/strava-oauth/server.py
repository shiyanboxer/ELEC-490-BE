# Strava tokens https://www.strava.com/settings/api

#!flask/bin/python
import logging

from flask import Flask, render_template, redirect, url_for, request, jsonify

# Enviroment variables 
# https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1
import os
from dotenv import load_dotenv

from stravalib import Client

app = Flask(__name__)
# app.config.from_envvar('APP_SETTINGS')
load_dotenv()

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET= os.getenv('STRAVA_CLIENT_SECRET')

@app.route("/")
def login():
    client = Client()
    # url = c.authorization_url(client_id=app.config['STRAVA_CLIENT_ID'],
    #                           redirect_uri=url_for('.logged_in', _external=True),
    #                           approval_prompt='auto')

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
        
        types = ['time', 'heartrate', 'temp']
        
         # Get all activity
         # https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities
        for activity in client.get_activities(after = "2010-01-01T00:00:00Z",  limit=5):
            print("{0.name} {0.moving_time}".format(activity))
            
            # Activities can have many streams, you can request n desired stream types
            stream = client.get_activity_streams(activity.id, types=types, resolution='medium')

            # Result is a dictionary object.  The dict's key are the stream type.
            if 'heartrate' in stream.keys():
                print(stream['heartrate'].data)
            
        return render_template('login_results.html', athlete=strava_athlete, access_token=access_token)


@app.route("/get_activity")
def get_activity():
    client = Client()
    
    # Get all activity
    for activity in client.get_activities(after = "2010-01-01T00:00:00Z",  limit=5):
        print("{0.name} {0.moving_time}".format(activity))
        
        # Activities can have many streams, you can request n desired stream types
        stream = client.get_activity_streams(activity.id, types=types, resolution='medium')

        # Result is a dictionary object.  The dict's key are the stream type.
        if 'heartrate' in stream.keys():
            print(stream['heartrate'].data)
            
    return

if __name__ == '__main__':
    app.run(debug=True)
