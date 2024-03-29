#!/usr/bin/env python3
"""Under the Bar - Plot Volume per Week

This file provides a plot of volume per week, can be optionally limited to the last year.
"""

import json
import os
import re
import matplotlib.pyplot as plt
import datetime as dt
from dateutil.relativedelta import relativedelta
import numpy as np
from pathlib import Path
# INIT




# Started with the cumulative reps graph as the starting point for this plot




def generate_options_volume_week(timelimit=False):
	# return every weight_reps type exercise ever completed by user
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
	
	# to include based on body weight where available. Add the specific exercises to this list
	special_bodyweight = ["Chin Up (Weighted)",
		"Chin Up",
		"Chin Up (Assisted)",
		"Pull Up (Weighted)",
		"Pull Up",
		"Pull Up (Assisted)",
		"Ring Dips",
		"Triceps Dip",
		"Triceps Dip (Weighted)",
		"Triceps Dip (Assisted)",
		"Chest Dip",
		"Chest Dip (Weighted)",
		"Chest Dip (Assisted)",
		]
	
	cal_start_date = None
	if timelimit == True:
		cal_start_date = dt.datetime.now().astimezone()-relativedelta(years=1)
		cal_start_date = (cal_start_date - dt.timedelta(days=(cal_start_date.isoweekday()%7))).strftime("%Y-%m-%d")
	
	# Find each workout json file	
	user_files = []	
	for userfile in sorted(os.listdir(workouts_folder), reverse=True):
		match_user_file = re.search('workout'+'_(....-..-..)_(.+).json',userfile)
		if match_user_file:
			workout_date=match_user_file.group(1)
			workout_id=match_user_file.group(2)
			#print("Found workout file for:",workout_date,workout_id,", in file",userfile)
			user_files.append(userfile)
			
			if timelimit and workout_date < cal_start_date:
				break
	print(len(user_files),"user data files to process")
	
	exercises_available = {}
	
	# add the all exercises option
	filename = user_folder+'/plot_volumeweek_all.svg'
	if timelimit:
		filename = user_folder+'/plot_volumeweekyear_all.svg'
	exists = os.path.exists(filename)
	exercises_available["--All--"] = exists
	
	for user_file in user_files:
		f = open(workouts_folder+"/"+user_file)
		workout_data = json.load(f)
		
		for set_group in workout_data['exercises']:
			if set_group["exercise_type"] == "weight_reps" or set_group["title"] in special_bodyweight:
			
				filename = user_folder+'/plot_volumeweek_'+re.sub(r'\W+', '', set_group["title"])+'.svg'
				if timelimit:
					filename = user_folder+'/plot_volumeweekyear_'+re.sub(r'\W+', '', set_group["title"])+'.svg'
				exists = os.path.exists(filename)
				exercises_available[set_group["title"]] = exists
				
				#print(set_group["title"],exists,filename)


	return exercises_available









def generate_plot_volume_week(the_exercise, width, height, timelimit=False):
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
	
	
	# Load bodyweight data if it is available 
	special_bodyweight = ["Chin Up (Weighted)",
		"Chin Up",
		"Chin Up (Assisted)",
		"Pull Up (Weighted)",
		"Pull Up",
		"Pull Up (Assisted)",
		"Ring Dips",
		"Triceps Dip",
		"Triceps Dip (Weighted)",
		"Triceps Dip (Assisted)",
		"Chest Dip",
		"Chest Dip (Weighted)",
		"Chest Dip (Assisted)",
		]
	bodyweight_data = {}
	bodyweight_dates = np.array([])
	if os.path.exists(user_folder+"/body_measurements.json"):
		with open(user_folder+"/body_measurements.json", 'r') as file:
			raw_data = json.load(file)
			for element in raw_data["data"]:
				if "weight_kg" in element.keys():
					bodyweight_data[int(element["date"].replace("-",""))] = element["weight_kg"]
					bodyweight_dates = np.append(bodyweight_dates, int(element["date"].replace("-","")))
	
	
	
	cal_start_date = None
	if timelimit == True:
		cal_start_date = dt.datetime.now().astimezone()-relativedelta(years=1)
		cal_start_date = (cal_start_date - dt.timedelta(days=(cal_start_date.isoweekday()%7))).strftime("%Y-%m-%d")


	# Find each workout json file	
	user_files = []	
	for userfile in sorted(os.listdir(workouts_folder), reverse=True):
		match_user_file = re.search('workout'+'_(....-..-..)_(.+).json',userfile)
		if match_user_file:
			workout_date=match_user_file.group(1)
			workout_id=match_user_file.group(2)
			#print("Found workout file for:",workout_date,workout_id,", in file",userfile)
			user_files.append(userfile)
			
			if timelimit and workout_date < cal_start_date:
				break
		
	print(len(user_files),"user data files to process")


	# Process each workout file to get each relevant exercise work out and set group
	exercise_to_track_setgroups = []
	exercise_to_track_dates = []
	exercise_to_track_workouts = {}
	for user_file in user_files:
		f = open(workouts_folder+"/"+user_file)
		workout_data = json.load(f)
		
		#parent_data = {}
		workout_date = workout_data['start_time']
		
		relevant_set_groups = []
		for set_group in workout_data['exercises']:
			if set_group["title"] == the_exercise or (the_exercise=="--All--" and (set_group["exercise_type"] == "weight_reps" or set_group["title"] in special_bodyweight)):
				relevant_set_groups.append(set_group)
			
		if len(relevant_set_groups)>0:
			exercise_to_track_workouts[workout_date] = relevant_set_groups
			
		
	print(len(exercise_to_track_workouts.keys()),"relevant user workouts to process")

	# Go through each set group of each workout to find total reps for the workout
	exercise_to_track_data = {}
	exercise_to_track_data_month = {}
	for workout_date in exercise_to_track_workouts.keys():
		repcount = 0
		
		for set_group in exercise_to_track_workouts[workout_date]:
		
			add_bodyweight = 0
			if set_group["title"] in special_bodyweight:
				use_date = int(dt.datetime.fromtimestamp(workout_date, dt.timezone.utc).strftime("%Y%m%d"))
				prev_dates = bodyweight_dates[bodyweight_dates < use_date]
				if len(prev_dates)>0:
					add_bodyweight = bodyweight_data[int(prev_dates.max())]
			
			
			for workout_set in set_group['sets']:
				if workout_set["weight_kg"] == None:
					workout_set["weight_kg"] = 0
				reps = workout_set["reps"] * (workout_set["weight_kg"]+add_bodyweight)
				if set_group["equipment_category"] == "dumbbell":
					reps = reps * 2
				
				repcount += reps
		#print("workout:",workout_date,repmax1,repmax3,repmax5,repmax10)
		exercise_to_track_data[workout_date]=repcount
		
		# week totals
		workout_week = dt.datetime.fromtimestamp(workout_date, dt.timezone.utc)
		workout_week = (workout_week - dt.timedelta(days=(workout_week.isoweekday()%7))).date()
		if workout_week in exercise_to_track_data_month.keys():
			exercise_to_track_data_month[workout_week] += repcount
		else:
			exercise_to_track_data_month[workout_week] = repcount

	#sys.exit()
	# Now re go through each workout in consecutive order to build cumulative chart
	repcount_data = []
	repcount_dates = []
	barchart_dates = []
	barchart_data = []
	count_reps = 0
	for workout_key in sorted(exercise_to_track_data.keys()):
		count_reps += exercise_to_track_data[workout_key]
		repcount_data.append(count_reps)
		repcount_dates.append(workout_key)
		barchart_dates.append(workout_key)
		barchart_data.append(exercise_to_track_data[workout_key])

	# do it for the months
	monthchart_dates = []
	monthchart_data = []
	for month_key in sorted(exercise_to_track_data_month.keys()):
		monthchart_dates.append(month_key)
		monthchart_data.append(exercise_to_track_data_month[month_key])

	#Create dates for each series x axis
	x_repcount = [dt.datetime.fromtimestamp(d, dt.timezone.utc).date() for d in repcount_dates]
	x_barchart = [dt.datetime.fromtimestamp(d, dt.timezone.utc).date() for d in barchart_dates]

	#Create plot
	plt.style.use('dark_background') # Can just comment out this line if don't want dark style.
	plt.rc('xtick', labelsize=8)
	plt.rc('ytick', labelsize=8)
	plt.rc('legend', fontsize=8) 
	fig, ax1 = plt.subplots()
	ax2 = ax1.twinx()

	ax1.step(x_repcount, repcount_data, where='post', label='Volume', alpha=0.8)
	ax1.text(x_repcount[-1], repcount_data[-1], int(repcount_data[-1]),fontsize=7,alpha=0.5)

	#ax2.bar(x_barchart,barchart_data,alpha=0.5,width=2)
	ax2.bar(monthchart_dates,monthchart_data,alpha=0.5,width=6,align='edge')

	#Plot formatting
	ax1.legend(loc='lower right')
	plt.title(the_exercise+' Volume (per Week)')
	ax1.set_xlabel("Generated "+str(dt.datetime.now())[:16], fontsize=8)
	fig1 = plt.gcf()
	size=fig1.get_size_inches()
	#fig1.set_size_inches(size[0]*2.5,size[1]*2)
	#fig1.set_size_inches(1600/fig1.dpi,1024/fig.dpi)
	fig.set_size_inches(width/fig1.dpi,height/fig.dpi)
	plt.tight_layout(pad=0.5)
	#plt.show()

	# Write to a folder change png to svg if want that
	if the_exercise == "--All--":
		the_exercise = "all"
	
	export_folder = user_folder
	if timelimit:
		fig1.savefig(export_folder+'/plot_volumeweekyear_'+re.sub(r'\W+', '', the_exercise)+'.svg', dpi=100)
	else:
		fig1.savefig(export_folder+'/plot_volumeweek_'+re.sub(r'\W+', '', the_exercise)+'.svg', dpi=100)


