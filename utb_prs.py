#!/usr/bin/env python3
"""Under the Bar - PRs

This file updates a local file with PRs

Provides 1RM, 5RM and 10RM
"""
import json
import os
import re
import matplotlib.pyplot as plt
import datetime as dt
import sys
from pathlib import Path



def do_the_thing():
	home_folder = str(Path.home())
	utb_folder = home_folder + "/.underthebar"
	session_data = {}
	if os.path.exists(utb_folder+"/session.json"):	
		with open(utb_folder+"/session.json", 'r') as file:
			session_data = json.load(file)
	else:
		return 403
	user_folder = utb_folder + "/user_" + session_data["user-id"]	
	workouts_folder = user_folder + "/workouts"

	their_user_id = session_data["user-id"]


	# Find each workout json file	
	user_files = []	
	for userfile in sorted(os.listdir(workouts_folder), reverse=True):
		match_user_file = re.search('workout'+'_(....-..-..)_(.+).json',userfile)
		if match_user_file:
			workout_date=match_user_file.group(1)
			workout_id=match_user_file.group(2)
			#print("Found workout file for:",workout_date,workout_id,", in file",userfile)
			user_files.append(userfile)
	print(len(user_files),"user data files to process")


	
	
	# Find each exercise available
	exercises_available = {}
	year_ago = dt.datetime.now().replace(year = dt.datetime.now().year - 1,hour=0,minute=0,second=0).timestamp()
	start_of_year = dt.datetime.now().replace(month=1,day=1,hour=0,minute=0,second=0).timestamp()
	start_of_last_year = dt.datetime.now().replace(year = dt.datetime.now().year - 1,month=1,day=1,hour=0,minute=0,second=0).timestamp()
	print("start of year", start_of_year)
	for user_file in user_files:
		f = open(workouts_folder+"/"+user_file)
		workout_data = json.load(f)
		workout_date = workout_data['start_time']
		
		for set_group in workout_data['exercises']:
			if set_group["title"] not in exercises_available.keys():
				exercises_available[set_group["title"]] = {"template_id":set_group["exercise_template_id"], "exercise_type":set_group["exercise_type"]}
			
			# either weight_reps, reps_only, bodyweight_reps, duration, distance_duration
			if set_group["exercise_type"] == "weight_reps":
				for workout_set in set_group['sets']:
					weight = workout_set["weight_kg"]
					reps = workout_set["reps"]
					
					if reps >= 1 and weight > exercises_available[set_group["title"]].get("best_weight",0):
						exercises_available[set_group["title"]]["best_weight"] = weight
						exercises_available[set_group["title"]]["best_weight_date"] = workout_date
					if reps >= 1 and workout_date > start_of_year and weight > exercises_available[set_group["title"]].get("best_weight_this_year",0):
						exercises_available[set_group["title"]]["best_weight_this_year"] = weight
						exercises_available[set_group["title"]]["best_weight_this_year_date"] = workout_date
					if reps >= 5 and weight > exercises_available[set_group["title"]].get("5_rep_max_weight",0):
						exercises_available[set_group["title"]]["5_rep_max_weight"] = weight
						exercises_available[set_group["title"]]["5_rep_max_weight_date"] = workout_date
					if reps >= 10 and weight > exercises_available[set_group["title"]].get("10_rep_max_weight",0):
						exercises_available[set_group["title"]]["10_rep_max_weight"] = weight
						exercises_available[set_group["title"]]["10_rep_max_weight_date"] = workout_date
			
			elif set_group["exercise_type"] == "reps_only" or set_group["exercise_type"] == "bodyweight_reps" :
				for workout_set in set_group['sets']:
					reps = workout_set["reps"]
					
					if reps > exercises_available[set_group["title"]].get("best_reps",0):
						exercises_available[set_group["title"]]["best_reps"] = reps
						exercises_available[set_group["title"]]["best_reps_date"] = workout_date
						
			elif set_group["exercise_type"] == "distance_duration":
				for workout_set in set_group['sets']:
					#print(workout_set)
					distance_meters = workout_set["distance_meters"]
					duration_seconds = workout_set["duration_seconds"]
					
					if distance_meters > exercises_available[set_group["title"]].get("best_distance",0):
						exercises_available[set_group["title"]]["best_distance"] = distance_meters
						exercises_available[set_group["title"]]["best_distance_date"] = workout_date
					if workout_date > start_of_year and distance_meters > exercises_available[set_group["title"]].get("best_distance_this_year",0):
						exercises_available[set_group["title"]]["best_distance_this_year"] = distance_meters
						exercises_available[set_group["title"]]["best_distance_this_year_date"] = workout_date
			
			
			elif set_group["exercise_type"] == "duration":
				for workout_set in set_group['sets']:
					#print(workout_set)
					duration_seconds = workout_set["duration_seconds"]
					
					if duration_seconds > exercises_available[set_group["title"]].get("best_duration",0):
						exercises_available[set_group["title"]]["best_duration"] = duration_seconds
						exercises_available[set_group["title"]]["best_duration_date"] = workout_date
					if workout_date > start_of_year and duration_seconds > exercises_available[set_group["title"]].get("best_duration_this_year",0):
						exercises_available[set_group["title"]]["best_duration_this_year"] = duration_seconds
						exercises_available[set_group["title"]]["best_duration_this_year_date"] = workout_date
			else:
				print("unhandled type:",set_group["exercise_type"])
			
	print(len(exercises_available.keys()),"user exercises found")
	#for exer in exercises_available.keys():
	#	print(exer, exercises_available[exer])
		
	# The main dict
	the_main_dict = {"data":[],"Etag":"local"}
	
	for exer in exercises_available.keys():
		if "best_weight" in exercises_available[exer]:
			record_dict = {"exercise_template_id": exercises_available[exer]["template_id"],
				"type": "best_weight","record": exercises_available[exer]["best_weight"],
				"date":exercises_available[exer]["best_weight_date"]}
			the_main_dict["data"].append(record_dict)
		if "best_weight_this_year" in exercises_available[exer]:
			record_dict = {"exercise_template_id": exercises_available[exer]["template_id"],
				"type": "best_weight_this_year","record": exercises_available[exer]["best_weight_this_year"],
				"date":exercises_available[exer]["best_weight_this_year_date"]}
			the_main_dict["data"].append(record_dict)
		if "5_rep_max_weight" in exercises_available[exer]:
			record_dict = {"exercise_template_id": exercises_available[exer]["template_id"],
				"type": "5_rep_max_weight","record": exercises_available[exer]["5_rep_max_weight"],
				"date":exercises_available[exer]["5_rep_max_weight_date"]}
			the_main_dict["data"].append(record_dict)
		if "10_rep_max_weight" in exercises_available[exer]:
			record_dict = {"exercise_template_id": exercises_available[exer]["template_id"],
				"type": "10_rep_max_weight","record": exercises_available[exer]["10_rep_max_weight"],
				"date":exercises_available[exer]["10_rep_max_weight_date"]}
			the_main_dict["data"].append(record_dict)
		if "best_reps" in exercises_available[exer]:
			record_dict = {"exercise_template_id": exercises_available[exer]["template_id"],
				"type": "best_reps","record": exercises_available[exer]["best_reps"],
				"date":exercises_available[exer]["best_reps_date"]}
			the_main_dict["data"].append(record_dict)
		if "best_distance" in exercises_available[exer]:
			record_dict = {"exercise_template_id": exercises_available[exer]["template_id"],
				"type": "best_distance","record": exercises_available[exer]["best_distance"],
				"date":exercises_available[exer]["best_distance_date"]}
			the_main_dict["data"].append(record_dict)
		if "best_distance_this_year" in exercises_available[exer]:
			record_dict = {"exercise_template_id": exercises_available[exer]["template_id"],
				"type": "best_distance_this_year","record": exercises_available[exer]["best_distance_this_year"],
				"date":exercises_available[exer]["best_distance_this_year_date"]}
			the_main_dict["data"].append(record_dict)
		if "best_duration" in exercises_available[exer]:
			record_dict = {"exercise_template_id": exercises_available[exer]["template_id"],
				"type": "best_duration","record": exercises_available[exer]["best_duration"],
				"date":exercises_available[exer]["best_duration_date"]}
			the_main_dict["data"].append(record_dict)
		if "best_duration_this_year" in exercises_available[exer]:
			record_dict = {"exercise_template_id": exercises_available[exer]["template_id"],
				"type": "best_duration_this_year","record": exercises_available[exer]["best_duration_this_year"],
				"date":exercises_available[exer]["best_duration_this_year_date"]}
			the_main_dict["data"].append(record_dict)
	
	with open(user_folder+"/"+"set_personal_records.json", 'w') as f:
		json.dump(the_main_dict, f)
		





if __name__ == "__main__":
	do_the_thing()
