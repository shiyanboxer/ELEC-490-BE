## ELEC 490 Backend
> **_NOTE:_** API and Database Schema Documentation can be found [here](https://docs.google.com/document/d/1no3cW1rfu7zmcbKZR0VY-XDIb4JYl5ykk_-kTJci6EE/edit?usp=sharing)

### [API Endpoint](https://elec49x.herokuapp.com/)
This is the backend component for the recovery tracker. It uses:
- Python 3.10.5
- Stavalib
- pip3
- requests
- json

### Stravalib
The **stravalib** Python package provides easy-to-use tools for accessing and 
downloading Strava data from the Strava V3 web service. Stravalib provides a Client class that supports:
* Authenticating with stravalib 
* Accessing and downloading strava activity, club and profile data 
* Making changes to account activities 

### Quick Start
```
git clone https://github.com/shiyanboxer/ELEC-490-BE.git
pip3 install -r requirements.txt.
create and setup a .env file with Strava access tokens
brew install mysql
pip3 install mysqlclient
python3 server.py
```

### Authentication

In order to make use of this library, you will need to create an app in Strava. 

```python
from stravalib.client import Client

client = Client()
authorize_url = client.authorization_url(client_id=1234, redirect_uri='http://localhost:8282/authorized')
# Have the user click the authorization URL, a 'code' param will be added to the redirect_uri
# .....

# Extract the code from your webapp response
code = requests.get('code') # or whatever your framework does
token_response = client.exchange_code_for_token(client_id=1234, client_secret='asdf1234', code=code)
access_token = token_response['access_token']
refresh_token = token_response['refresh_token']
expires_at = token_response['expires_at']

# Now store that short-lived access token somewhere (a database?)
client.access_token = access_token
# You must also store the refresh token to be used later on to obtain another valid access token
# in case the current is already expired
client.refresh_token = refresh_token

# An access_token is only valid for 6 hours, store expires_at somewhere and
# check it before making an API call.
client.token_expires_at = expires_at

athlete = client.get_athlete()
print("For {id}, I now have an access token {token}".format(id=athlete.id, token=access_token))

# ... time passes ...
if time.time() > client.token_expires_at:
    refresh_response = client.refresh_access_token(client_id=1234, client_secret='asdf1234',
        refresh_token=client.refresh_token)
    access_token = refresh_response['access_token']
    refresh_token = refresh_response['refresh_token']
    expires_at = refresh_response['expires_at']
```

### Athletes and Activities

(This is a glimpse into what you can do.)

```python
# Currently-authenticated (based on provided token) athlete
# Will have maximum detail exposed (resource_state=3)
curr_athlete = client.get_athlete()

# Fetch another athlete
other_athlete = client.get_athlete(123)
# Will only have summary-level attributes exposed (resource_state=2)

# Get an activity
activity = client.get_activity(123)
# If activity is owned by current user, will have full detail (resource_state=3)
# otherwise summary-level detail.
```

### Streams

Streams represent the raw data of the uploaded file. Activities, efforts, and
segments all have streams. There are many types of streams, if activity does
not have requested stream type, returned set simply won't include it.

```python

# Activities can have many streams, you can request n desired stream types
types = ['time', 'latlng', 'altitude', 'heartrate', 'temp', ]

streams = client.get_activity_streams(123, types=types, resolution='medium')

#  Result is a dictionary object.  The dict's key are the stream type.
if 'altitude' in streams.keys():
    print(streams['altitude'].data)

```