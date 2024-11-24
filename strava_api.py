from pathlib import Path
import os
import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import sys
from stravalib import Client
from datetime import datetime
import requests, json
import webbrowser
import uuid
import random

class Server(socketserver.TCPServer):

    # Avoid "address already used" error when frequently restarting the script 
    allow_reuse_address = True


class Handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            code_value = str(parse_qs(urlparse(self.path).query)["code"][0])
            self.send_response(200, "OK")
            self.end_headers()
            self.wfile.write("It worked! Code returned, you can close the browser window.".encode("utf-8"))

            print("Writing strava code to file")

            home_folder = str(Path.home())
            utb_folder = home_folder + "/.underthebar"
            session_data = {}
            if os.path.exists(utb_folder+"/session.json"):	
                with open(utb_folder+"/session.json", 'r') as file:
                    session_data = json.load(file)
                    session_data["strava-token-code"] = code_value
                with open(utb_folder+"/session.json", 'w') as file:
                    json.dump(session_data,file)

        except:
            
            self.send_response(200, "OK")
            self.end_headers()
            self.wfile.write("Failed. Didn't find code.".encode("utf-8"))

	# note had to add this to allow server to work properly when run in window without console
    def log_message(self, format, *args):
        return



def do_the_thing():
	print("starting strava_api > do_the_thing()")

	#
	# THIS IS WHERE YOU ADD THE STRAVA API DETAILS
	#
	cl_id = None   # put you strava api client id here
	cl_secret = None  # put your strava api client secret here
	

	
	if cl_id == None or cl_secret == None:
		print("NEED TO ADD YOUR STRAVA API DETAILS TO strava_api.py !!!\n"*5)
		return 404

	get_token_url = False
	get_token_refresh = False
	get_token_access = True

	# things for Hevy
	BASIC_HEADERS = {
		'x-api-key': 'with_great_power',
		'Content-Type': 'application/json',
		'accept-encoding':'gzip'
	}

	# JSON of a basic running workout, we'll just adjust this
	run_template = {
	  "workout": {
		"clientId": None,
		"name": "Running (import)",
		"description": "(Import from Strava)",
		"imageUrls": [],
		"exercises": [
		  {
			"title": "Running",
			"id": "AC1BB830",
			"autoRestTimerSeconds": 0,
			"notes": "",
			"routineNotes": "",
			"sets": [
			  {
				"index": 0,
				"completed": True,
				"indicator": "normal",
				"weight": None,
				"reps": None,
				"distance": 3200,
				"duration": 1453
			  }
			]
		  }
		],
		"startTime": 1644300575,
		"endTime": 1644302088,
		"useAutoDurationTimer": True,
		"trackWorkoutAsRoutine": False,
#		"isPrivate": True, # allows testing without spamming ppls feeds
		"appleWatch": False
	  },
	  "emptyResponse": True,
	  "updateRoutineValues": False,
	  "shareToStrava": False
	}




	# Check if we're logged in to strava
	# The folder to access/store data files
	home_folder = str(Path.home())
	utb_folder = home_folder + "/.underthebar"
	session_data = {}
	if os.path.exists(utb_folder+"/session.json"):	
		with open(utb_folder+"/session.json", 'r') as file:
			session_data = json.load(file)
	else:
		pass
	if "strava-token-refresh" in session_data:
		get_token_url = False
		print("Strava already logged in")
	else:
		get_token_url = True
		print("Strava not logged in")




	client = Client()

	# If we're not logged in first step is to get a URL and go to the web browser
	if get_token_url:
		url = client.authorization_url(client_id=cl_id, redirect_uri='http://localhost:8888/authorization',scope=['activity:read'])#'read_all','profile:read_all',
		

		print(url)
		#print("Go to the url and with dev tools obtain the returned 'code'. Update this file.")
		
		webbrowser.open(url, new=1, autoraise=True)
		#sys.exit()

		# Here we run a web server to catch the redirect from strava, single request server only
		print("Waiting for web browser response ....")
		with Server(("", 8888), Handler) as httpd:
			httpd.handle_request()

		# The server class receives and writes an access code to our session file, so reload it
		if os.path.exists(utb_folder+"/session.json"):	
			with open(utb_folder+"/session.json", 'r') as file:
				session_data = json.load(file)

		get_token_refresh = True
		#sys.exit()

	# Next part of logging in is to get current refresh/access tokens using the code we received
	if get_token_refresh:
		token_response = client.exchange_code_for_token(client_id=cl_id,
												  client_secret=cl_secret,
												  #code=cl_code)
												  code=session_data["strava-token-code"])
		access_token = token_response['access_token']
		refresh_token = token_response['refresh_token']
		#print("access:",access_token,"\nrefresh:",refresh_token)
		client = Client(access_token=access_token)

		session_data["strava-token-refresh"] = refresh_token
		with open(utb_folder+"/session.json", 'w') as file:
			json.dump(session_data,file)
		get_token_access = False
	#    sys.exit()
	#sys.exit()

	# If we were already logged in, we use the stored refresh token to get an access token
	if get_token_access:
		token_response = client.refresh_access_token(client_id=cl_id,
										  client_secret=cl_secret,
										  #refresh_token=cl_refresh)
										  refresh_token=session_data["strava-token-refresh"])
		new_access_token = token_response['access_token']
		#print("access:",new_access_token)
		client = Client(access_token=new_access_token)


	# At this point we should be entirely logged in to Strava
	# So retrieve a list of most recent activities, then go through to get the latest submittable
	athlete = client.get_athlete()
	print("Hello from Strava, {}".format(athlete.firstname))
	activities = client.get_activities(limit=10)
	for activity in activities:
		#print("{0.type} {0.moving_time} {0.distance} {0.start_date} {0.average_heartrate} {0.max_heartrate} {0.average_watts} {0.max_watts}".format(activity))
		print(activity.type,activity.name, activity.start_date)
		#print(str(activity.type) == "root='Run'")
		#print(type(activity.type))
		# Here handle the submittable activities, we only want to submit one of those
		# For the activity we want we'll modify the hevy workout template
		do_submit = False
		if activity.type == "Run" or str(activity.type) == "root='Run'":
			run_template["workout"]["name"] = activity.name
			run_template["workout"]["exercises"][0]["title"] = "Running"
			run_template["workout"]["exercises"][0]["id"] = "AC1BB830"

			run_template["workout"]["startTime"] = int(activity.start_date.timestamp())
			run_template["workout"]["endTime"] = int(activity.start_date.timestamp()+activity.moving_time.total_seconds())
			run_template["workout"]["exercises"][0]["sets"][0]["duration"] = int(activity.moving_time.total_seconds())
			run_template["workout"]["exercises"][0]["sets"][0]["distance"] = int(activity.distance)
			
			run_template["workout"]["description"] = "Running" + "\n\n"+run_template["workout"]["description"]
			if activity.average_heartrate:
				run_template["workout"]["exercises"][0]["notes"] = "Heartrate Avg: " + str(activity.average_heartrate) + "bpm, Max: " + str(activity.max_heartrate) + "bpm."

			#print("got a run to submit")
			do_submit = True        

		# Note that this is a custom exercise that only exists for me in Hevy...
		elif ((activity.type == "VirtualRide" or str(activity.type) == "root='VirtualRide'") and
				session_data["user-id"] == "f21f5af1-a602-48f0-82fb-ed09bc984326"):
			run_template["workout"]["name"] = activity.name #"Virtual Ride (import)"
			run_template["workout"]["exercises"][0]["title"] = "Cycling (Virtual)"
			run_template["workout"]["exercises"][0]["id"] = "89f3ed93-5418-4cc6-a114-0590f2977ae8"

			run_template["workout"]["startTime"] = int(activity.start_date.timestamp())
			run_template["workout"]["endTime"] = int(activity.start_date.timestamp()+activity.moving_time.total_seconds())
			run_template["workout"]["exercises"][0]["sets"][0]["duration"] = int(activity.moving_time.total_seconds())
			run_template["workout"]["exercises"][0]["sets"][0]["distance"] = int(activity.distance)
			
			run_template["workout"]["description"] = "Cycling (Virtual)" + "\n\n"+run_template["workout"]["description"]
			if activity.average_heartrate:
				run_template["workout"]["exercises"][0]["notes"] = "Heartrate Avg: " + str(activity.average_heartrate) + "bpm, Max: " + str(activity.max_heartrate) + "bpm."
			if activity.average_watts:
				run_template["workout"]["exercises"][0]["notes"] += "\nPower Avg: " + str(activity.average_watts) + "W, Max: " + str(activity.max_watts) + "W."
			
			#print(run_template)
			do_submit = True

		elif activity.type == "Ride" or str(activity.type) == "root='Ride'":
			run_template["workout"]["name"] = activity.name 
			run_template["workout"]["exercises"][0]["title"] = "Cycling"
			run_template["workout"]["exercises"][0]["id"] = "D8F7F851"

			run_template["workout"]["startTime"] = int(activity.start_date.timestamp())
			run_template["workout"]["endTime"] = int(activity.start_date.timestamp()+activity.moving_time.total_seconds())
			run_template["workout"]["exercises"][0]["sets"][0]["duration"] = int(activity.moving_time.total_seconds())
			run_template["workout"]["exercises"][0]["sets"][0]["distance"] = int(activity.distance)
			
			run_template["workout"]["description"] = "Cycling" + "\n\n"+run_template["workout"]["description"]
			if activity.average_heartrate:
				run_template["workout"]["exercises"][0]["notes"] = "Heartrate Avg: " + str(activity.average_heartrate) + "bpm, Max: " + str(activity.max_heartrate) + "bpm."
			if activity.average_watts:
				run_template["workout"]["exercises"][0]["notes"] += "\nPower Avg: " + str(activity.average_watts) + "W, Max: " + str(activity.max_watts) + "W."
			
			#print(run_template)
			do_submit = True

		# Standard walk exercise
		elif activity.type == "Walk" or str(activity.type) == "root='Walk'":
			run_template["workout"]["name"] = activity.name #"Walk (import)"
			run_template["workout"]["exercises"][0]["title"] = "Walking"
			run_template["workout"]["exercises"][0]["id"] = "33EDD7DB"

			run_template["workout"]["startTime"] = int(activity.start_date.timestamp())
			run_template["workout"]["endTime"] = int(activity.start_date.timestamp()+activity.moving_time.total_seconds())
			run_template["workout"]["exercises"][0]["sets"][0]["duration"] = int(activity.moving_time.total_seconds())
			run_template["workout"]["exercises"][0]["sets"][0]["distance"] = int(activity.distance)
			
			run_template["workout"]["description"] = "Walking" + "\n\n"+run_template["workout"]["description"]
			if activity.average_heartrate:
				run_template["workout"]["exercises"][0]["notes"] = "Heartrate Avg: " + str(activity.average_heartrate) + "bpm, Max: " + str(activity.max_heartrate) + "bpm."
			
			#print(run_template)
			do_submit = True

		# Now log in to Hevy and do the submission
		if do_submit:
			do_submit = False

			import hevy_api
			user_data = hevy_api.is_logged_in()
			if user_data[0] == False:
				print("403")
				sys.exit()
			user_folder = user_data[1]
			auth_token = user_data[2]
			
			
			s = requests.Session()
			s.headers.update({'auth-token': auth_token})
			headers = BASIC_HEADERS.copy()

			r = s.get("https://api.hevyapp.com/account", headers=headers)
			data = r.json()
			username = data["username"]
			print("Hello from Hevy,",username)
			my_user_id = data["id"]
			#run_template["workout"]["clientId"] = my_user_id # This is wrong, we just want a random uuid it seems
			
			# generate uuid using workout start time as seed, so is repeatable (might prevent submitting duplicates?)
			rnd = random.Random()
			rnd.seed(run_template["workout"]["startTime"])
			local_id = uuid.UUID(int=rnd.getrandbits(128), version=4)
			run_template["workout"]["clientId"] = str(local_id)
			
			#run_template["workout"]["clientId"] = str(uuid.uuid4()) # or totally random id


			print("\n",json.dumps(run_template,indent=4),"\n")
			#sys.exit()

			r = s.post('https://api.hevyapp.com/workout', data=json.dumps(run_template), headers=headers)
			print(r)
			#sys.exit()
			break
		


	print("success")
	return 200

if __name__ == "__main__":
	do_the_thing()