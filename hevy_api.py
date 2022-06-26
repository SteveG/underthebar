#!/usr/bin/env python3
"""Hevy API

Provides the methods for interacting with the Hevy API
"""

import requests
import json
import os
import getpass
import re
import time
import datetime
import shutil

from pathlib import Path
import concurrent.futures 

# Basic headers to use throughout
BASIC_HEADERS = {
	'x-api-key': 'with_great_power',
	'Content-Type': 'application/json',
	'accept-encoding':'gzip'
}

#
# Simple method to provide a login prompt on command line, which is then just passed to login below
#
def login_cli():
	user = input("Please input a username: ")
	password = getpass.getpass()
	
	login(user,password)

#
# Login method taking a username and password
# Logs in and then downloads account.json, the profile pic, and the workout_count
# Returns 200 if all successful
#	
def login(user, password):
	home_folder = str(Path.home())
	utb_folder = home_folder + "/.underthebar"

	if not os.path.exists(utb_folder):
		os.makedirs(utb_folder)
		os.makedirs(utb_folder+"/temp")

	headers = BASIC_HEADERS.copy()
	
	# Post username and password to Hevy
	s = requests.Session()
	
	r = s.post('https://api.hevyapp.com/login', data=json.dumps({'emailOrUsername':user,'password':password}), headers=headers)
	if r.status_code == 200:
		json_content = r.json()
		s.headers.update({'auth-token': json_content['auth_token']})
		
		auth_token = json_content['auth_token']
	
		r = s.get("https://api.hevyapp.com/account", headers=headers)
		if r.status_code == 200:
			data = r.json()
			
			account_data = {"data":data, "Etag":r.headers['Etag']}
			#print(json.dumps(r.json(), indent=4, sort_keys=True))
			
			user_id = data["id"]
			
			user_folder = utb_folder + "/user_"+user_id
	
			if not os.path.exists(user_folder):
				os.makedirs(user_folder)
				os.makedirs(user_folder+"/workouts")
			
			with open(utb_folder+"/session.json", 'w') as f:
				json.dump({"auth-token":auth_token,"user-id":user_id},f)
			
			with open(user_folder+"/account.json", 'w') as f:
				json.dump(account_data, f)
				
			imageurl = data["profile_pic"]
			response = requests.get(imageurl, stream=True)
			if response.status_code == 200:
				with open(user_folder+"/profileimage", 'wb') as out_file:
					shutil.copyfileobj(response.raw, out_file)
    				
				r = s.get("https://api.hevyapp.com/workout_count", headers=headers)
				if r.status_code == 200:
					data = r.json()
					
					workout_count = {"data":data, "Etag":r.headers['Etag']}
					#print(json.dumps(r.json(), indent=4, sort_keys=True))
					
					with open(user_folder+"/workout_count.json", 'w') as f:
						json.dump(workout_count, f)
						
					return 200
				return r.status_code
		else:
			return r.status_code
	else:
    		return r.status_code

#
# Simple method to log out. We'll delete the user id and auth-token from the sessions file
#
def logout():
	# The folder to access/store data files
	home_folder = str(Path.home())
	utb_folder = home_folder + "/.underthebar"
	session_data = {}
	if os.path.exists(utb_folder+"/session.json"):	
		with open(utb_folder+"/session.json", 'r') as file:
			session_data = json.load(file)
	else:
		return True
	del session_data["auth-token"]
	del session_data["user-id"]
	with open(utb_folder+"/session.json", 'w') as f:
		json.dump({},f)
	return True

#
# Simple check to see if we have a current token saved indicating we are logged in
# If logged in return (True, User_Folder, Auth_Token) else (False, None, None)
#
def is_logged_in():
	# The folder to access/store data files
	home_folder = str(Path.home())
	utb_folder = home_folder + "/.underthebar"
	
	session_data = {}
	if os.path.exists(utb_folder+"/session.json"):	
		with open(utb_folder+"/session.json", 'r') as file:
			session_data = json.load(file)
	else:
		return False, None, None
	
	try:
		auth_token = session_data["auth-token"]
		# this is the folder we'll save the data file to
		user_folder = utb_folder + "/user_" + session_data["user-id"]	
		return True, user_folder, auth_token
	except:
		return False, None, None

#
# Updates a local JSON file and returns a http status code indicating success.
# to_update is the API call to be used. Needs to be from pre-determined list as below in lookup dict.
# API returns a 304 if local file is already up-to-date, or a 200 when providing a new file
# We add 404 for when asking for an unknown API call, and 403 when we are not logged in
#
def update_generic(to_update):
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# The accessible API calls for this method
	lookup = {"account":"https://api.hevyapp.com/account",
		"user_preferences":"https://api.hevyapp.com/user_preferences",
		"body_measurements":"https://api.hevyapp.com/body_measurements",
		"workout_count":"https://api.hevyapp.com/workout_count",
		"set_personal_records":"https://api.hevyapp.com/set_personal_records",
		"user_subscription":"https://api.hevyapp.com/user_subscription",
		}
	# Fail if to_update is not in the list
	if to_update not in lookup.keys():
		return 404
	
	update_url = lookup[to_update]
	filename = to_update + ".json"

	# Create headers to be used
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	
	# Check if the file already exists, if it does we'll send the server the Etag so we only get an update
	update_data = None
	if os.path.exists(user_folder+"/"+filename):	
		with open(user_folder+"/"+filename, 'r') as file:
			update_data = json.load(file)
		headers["if-none-match"] = update_data["Etag"]
	
	# Now finally do the request for the update. If new update then put that in the file and return 200, else return 304
	s = requests.Session()
	r = s.get(update_url, headers=headers)
	if r.status_code == 200:
		data = r.json()
		new_data = {"data":data, "Etag":r.headers['Etag']}
		with open(user_folder+"/"+filename, 'w') as f:
			json.dump(new_data, f)
		return 200
	elif r.status_code == 304:
		return 304

#
# Batch downloads JSON workout files
# This should be used when wanting to bulk download workout files.
# It finds the highest Hevy index in existing downloaded files and requests all new files after that index
# Hevy returns a number of workout files. Idea is to keep calling this until Hevy doesn't return anything.
#
def batch_download():
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]

	# Workouts subfolder
	workouts_folder = user_folder + "/workouts"
	
	# Create the headers to be used
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token	
	
	# We need to find the highest Hevy workout index in the existing data
	# Last created file won't work if user creates a workout in the past, so go through every file
	fileslist = sorted(os.listdir(workouts_folder))
	localWorkoutCount = len(fileslist)
	
	startIndex = 0
	# brute force which workout has largest index.
	if localWorkoutCount != 0:
		for file in fileslist:
			match_workout = re.search('^workout_([A-Za-z0-9_-]+).json\Z',file)
			if match_workout:
				with open(workouts_folder+"/"+file, 'r') as file:
					temp_data = json.load(file)
					temp_index = temp_data["index"]
					if temp_index >= startIndex:
						startIndex = temp_index +1 # make the start index one after the largest we have
	
	# Now finally do the request for workout files		
	s = requests.Session()	
	r = s.get("https://api.hevyapp.com/workouts_batch/"+str(startIndex), headers=headers)
	if r.status_code == 200:
		data = r.json()
		
		havesome = False
		for new_workout in data:
			havesome = True
			date_string = datetime.datetime.fromtimestamp(new_workout['start_time']).strftime('%Y-%m-%d')
			workoutfilename=workouts_folder+"/"+"workout_"+date_string+"_"+str(new_workout['short_id'])+".json"
			updated_time = int(time.mktime(time.strptime(new_workout['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')))
			with open(workoutfilename, 'w') as f:
				json.dump(new_workout, f)
			accesstime = int(time.mktime(time.gmtime()))
			os.utime(workoutfilename, (accesstime, updated_time-0))
			
			print("new workout",workoutfilename)

		# return 200 and a boolean indicating whether Hevy returned new files
		return 200, havesome
	else:
		return r.status_code, False

#
# This uploads all local workout ids and when they were last updated, hevy then returns any changes that have been made on server	
# This should be used when just wanting to get the most recent updates
# It seems inefficient when there are lots of workouts, but I guess any file could be updated at any time...
# Hevy returns isMore indicating whether this should be rerun to collect more updates
#
def workouts_sync_batch():
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	
	# Workouts subfolder	
	workouts_folder = user_folder + "/workouts"
	
	# Create required headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	
	# Go through all workouts and compile the workout ID and when it was updated
	existing_data = {}
	existing_id_file = {}
	for file in os.listdir(workouts_folder):
		match_workout = re.search('^workout_([A-Za-z0-9_-]+).json\Z',file)
		if match_workout:
			
			f = open(workouts_folder+'/'+file)
			workout_data = json.load(f)
			existing_data[workout_data['id']] = workout_data['updated_at']
			existing_id_file[workout_data['id']] = file
	
	# Post our existing data that we have compiled, and see what gets returned
	s = requests.Session()
	r = s.post('https://api.hevyapp.com/workouts_sync_batch', data=json.dumps(existing_data), headers=headers)
	json_content = r.json()	

	# Save any workouts returned to file, overwriting the old file if it existed
	for updated_workout in json_content['updated']:
		date_string = datetime.datetime.fromtimestamp(updated_workout['start_time']).strftime('%Y-%m-%d')
		workoutfilename=workouts_folder+"/"+"workout_"+date_string+"_"+str(updated_workout['short_id'])+".json"
		updated_time = int(time.mktime(time.strptime(updated_workout['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')))
		with open(workoutfilename, 'w') as f:
			json.dump(updated_workout, f)
		accesstime = int(time.mktime(time.gmtime()))
		os.utime(workoutfilename, (accesstime, updated_time-0))
		
		print("updated",workoutfilename)
		
	# Any workouts deleted we'll move our copy of the workout to a deleted folder	
	for deleted_workout in json_content['deleted']:
		deletedir = user_folder+"/deleted"
		if not os.path.exists(deletedir):
			os.makedirs(deletedir)
		print("delete", deleted_workout, existing_id_file[deleted_workout])
		shutil.move(workouts_folder+"/"+existing_id_file[deleted_workout],deletedir+"/"+existing_id_file[deleted_workout])
		
	# Do we need to make this API call again because there is more data available???
	update = False
	if json_content['isMore'] == True:
		update=True	
	
	return (200,update)

#	
# Get the Hevy workout feed starting from workout with given index, returns json data
#
def feed_workouts_paged(start_from):
	print("feed_workouts_paged",start_from)
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# workout image stuff, set folder, delete old images
	img_folder = str(Path.home())+ "/.underthebar/temp/"
	if not os.path.exists(img_folder):
		os.makedirs(img_folder)
	# its probably a bit much to do this every time, I'll put it somewhere else.
	#for f in os.listdir(img_folder):
	#	if os.stat(os.path.join(img_folder,f)).st_mtime < time.time() - 14 * 86400:
	#		os.remove(os.path.join(img_folder,f))
			
	# Make the headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	
	
	url = "https://api.hevyapp.com/feed_workouts_paged/"
	if start_from != 0:
		url = url + str(start_from)
	
	# Do the request
	s = requests.Session()	
	r = s.get(url, headers=headers)
	if r.status_code == 200:
	
		data = r.json()
		new_data = {"data":data, "Etag":r.headers['Etag']}
		
		# this bit is for downloading feed workout images, request in parallel
		img_urls = []
		for workout in data["workouts"]:
			for img_url in workout["image_urls"]:
				img_urls.append(img_url)
		
		with concurrent.futures.ThreadPoolExecutor() as exector : 
			exector.map(download_img, img_urls)
				
		return new_data
	
	elif r.status_code == 304:
		return 304


def download_img(img_url):
	try:
		img_folder = str(Path.home())+ "/.underthebar/temp/"
		file_name = img_url.split("/")[-1]
		print("start_img: "+file_name)
		if not os.path.exists(img_folder+file_name):
			response = requests.get(img_url, stream=True)
			with open(img_folder+file_name, 'wb') as out_file:
				shutil.copyfileobj(response.raw, out_file)
			del response
		print("end_img: "+file_name)
	except Exception as e:
		print(e)

#	
# Likes, or unlikes, a workout with the given id	
#
def like_workout(workout_id, like_it):
	print("like the workout", workout_id, like_it)
	# Make sure user is logged in, have their folder, and auth-token
	user_data = is_logged_in()
	if user_data[0] == False:
		return 403
	user_folder = user_data[1]
	auth_token = user_data[2]
	
	# Make the headers
	headers = BASIC_HEADERS.copy()
	headers["auth-token"] = auth_token
	
	
	url = "https://api.hevyapp.com/workout/like/"+workout_id
	if not like_it:
		url = "https://api.hevyapp.com/workout/unlike/"+workout_id
	
	s = requests.Session()	
	r = s.post(url, headers=headers)
	
	return r.status_code
	
	
	
	
	
	

if __name__ == "__main__":
	#login_cli()
	#print("updating account",update_generic("account"))
	#print("updating user_preferences",update_generic("user_preferences"))
	#print("updating workout_count",update_generic("workout_count"))
	#print("updating set_personal_records",update_generic("set_personal_records"))
	#print("updating user_subscription",update_generic("user_subscription"))
	print(is_logged_in())

