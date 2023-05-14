#!/usr/bin/env python3
"""Under the Bar - Plot Volume per Month

This file provides a plot of volume per month.
"""

import json
import os
import re
import matplotlib.pyplot as plt
import datetime as dt
from collections import Counter
from pathlib import Path
import numpy as np
# INIT




# Started with the cumulative reps graph as the starting point for this plot




def generate_options_volume_month():
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
	
	exercises_available = {}
	
	# add the all exercises option
	filename = user_folder+'/plot_volumemonth_all.svg'
	exists = os.path.exists(filename)
	exercises_available["--All--"] = exists
	# add the all exercises option
	filename = user_folder+'/plot_volumemonth_all_bodypart.svg'
	exists = os.path.exists(filename)
	exercises_available["--All-- (1. Body part)"] = exists
	# add the all exercises option
	filename = user_folder+'/plot_volumemonth_all_bodypartprop.svg'
	exists = os.path.exists(filename)
	exercises_available["--All-- (2. Body part prop)"] = exists
	
	for user_file in user_files:
		f = open(workouts_folder+"/"+user_file)
		workout_data = json.load(f)
		
		for set_group in workout_data['exercises']:
			if set_group["exercise_type"] == "weight_reps" or set_group["title"] in special_bodyweight:#
			
				filename = user_folder+'/plot_volumemonth_'+re.sub(r'\W+', '', set_group["title"])+'.svg'
				exists = os.path.exists(filename)
				exercises_available[set_group["title"]] = exists
				
				#print(set_group["title"],exists,filename)

	
	return exercises_available









def generate_plot_volume_month(the_exercise, width, height):
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

	# Go through each set group of each workout to find total volume for the workout
	exercise_to_track_data = {}
	exercise_to_track_data_month = {}
	bodypart_track_data_month = {}
	bodypart_counter = Counter()
	for workout_date in exercise_to_track_workouts.keys():
		repcount = 0
		workout_bodypart_counter = Counter()
		for set_group in exercise_to_track_workouts[workout_date]:
			
			add_bodyweight = 0
			if set_group["title"] in special_bodyweight:
				use_date = int(dt.datetime.fromtimestamp(workout_date, dt.timezone.utc).strftime("%Y%m%d"))
				prev_dates = bodyweight_dates[bodyweight_dates < use_date]
				if len(prev_dates)>0:
					add_bodyweight = bodyweight_data[int(prev_dates.max())]
			
			#print(set_group["muscle_group"])
			for workout_set in set_group['sets']:
				if workout_set["weight_kg"] == None:
					workout_set["weight_kg"] = 0
				reps = workout_set["reps"] * (workout_set["weight_kg"]+add_bodyweight)
			
				#reps = workout_set["reps"] * workout_set["weight_kg"]
				if set_group["equipment_category"] == "dumbbell":
					reps = reps * 2
				
				repcount += reps
				bodypart_counter.update({set_group["muscle_group"]:reps})
				workout_bodypart_counter.update({set_group["muscle_group"]:reps})
		
		#print("workout:",workout_date,repmax1,repmax3,repmax5,repmax10)
		#print(repcount,workout_bodypart_counter.total())
		exercise_to_track_data[workout_date]=repcount
		
		# month totals
		workout_month = dt.datetime.fromtimestamp(workout_date, dt.timezone.utc)
		workout_month = workout_month.replace(day=1).date()
		if workout_month in exercise_to_track_data_month.keys():
			exercise_to_track_data_month[workout_month] += repcount
			bodypart_track_data_month[workout_month].update(workout_bodypart_counter)
		else:
			exercise_to_track_data_month[workout_month] = repcount
			bodypart_track_data_month[workout_month] = workout_bodypart_counter
		#print(exercise_to_track_data_month[workout_month],bodypart_track_data_month[workout_month].total())
	
	

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
		
		
			
	#bodypart stuff
	#print(bodypart_counter)
	bodypart_list = sorted(list(bodypart_counter))
	bodypart_arrays = []
	for x in range(len(bodypart_list)):
		bodypart_arrays.append([])	

	# do it for the months
	monthchart_dates = []
	monthchart_data = []
	for month_key in sorted(exercise_to_track_data_month.keys()):
		monthchart_dates.append(month_key)
		monthchart_data.append(exercise_to_track_data_month[month_key])
		
		#bodypart stuff
		sumbody = 0
		for x in range(len(bodypart_list)):
			#bodypart_arrays[x].append(bodypart_track_data_month[month_key][bodypart_list[x]])
			#print(bodypart_track_data_month[month_key][bodypart_list[x]])
			sumbody += bodypart_track_data_month[month_key][bodypart_list[x]]
			if the_exercise == "--All-- (2. Body part prop)":
				#proportionate 
				if bodypart_track_data_month[month_key].total() == 0:
					bodypart_arrays[x].append(0)
				else:
					proportion = float(bodypart_track_data_month[month_key][bodypart_list[x]]) / float(bodypart_track_data_month[month_key].total())
					bodypart_arrays[x].append(proportion)
			else:
				bodypart_arrays[x].append(bodypart_track_data_month[month_key][bodypart_list[x]])
			
		print(monthchart_data[-1],sumbody)


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
	#ax2.bar(monthchart_dates,monthchart_data,alpha=0.5,width=25,align='edge')
	
	
	if the_exercise == "--All-- (1. Body part)" or the_exercise == "--All-- (2. Body part prop)":
		#bodypart stuff
		barbottom = [0] * len(bodypart_arrays[0])
		
		for x in range(len(bodypart_list)):
			print("lengths",len(barbottom), len(bodypart_arrays[x]))
			ax2.bar(monthchart_dates,bodypart_arrays[x],width=25,align='edge',bottom=barbottom,label=bodypart_list[x])
			c=[]
			for y in range(len(bodypart_arrays[0])):
				c.append(barbottom[y]+bodypart_arrays[x][y])
			barbottom = c
	#		if x==0:
	#			ax2.bar(monthchart_dates,bodypart_arrays[x],width=25,align='edge',label=bodypart_list[x])
	#		else:
	#			ax2.bar(monthchart_dates,bodypart_arrays[x],width=25,align='edge',bottom=bodypart_arrays[x-1],label=bodypart_list[x])
		#ax2.legend(loc='upper left')
		handles, labels = ax2.get_legend_handles_labels()
		ax2.legend(reversed(handles), reversed(labels), loc='upper left')
	else:
		ax2.bar(monthchart_dates,monthchart_data,alpha=0.5,width=25,align='edge')

	#Plot formatting
	ax1.legend(loc='lower right')
	plt.title(the_exercise+' Volume (per Month)')
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
	elif the_exercise == "--All-- (1. Body part)":
		the_exercise = "all_bodypart"
	elif the_exercise == "--All-- (2. Body part prop)":
		the_exercise = "all_bodypartprop"
	
	export_folder = user_folder
	fig1.savefig(export_folder+'/plot_volumemonth_'+re.sub(r'\W+', '', the_exercise)+'.svg', dpi=100)


