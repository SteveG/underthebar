#!/usr/bin/env python3
"""Under the Bar - Plot Rep Max (Year)

This file provides a plot of set rep max achievements, limited to the last year.

Includes 1RM, 3RM, 5RM, 10RM, along with estimated 1RM using Brzyki and Epley calculations.
"""

import json
import os
import re
import matplotlib.pyplot as plt
import datetime as dt
from dateutil.relativedelta import relativedelta

from pathlib import Path

# INIT
def generate_options_rep_max_year():
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
	
	# work out a year ago
	year_ago = dt.datetime.now() - relativedelta(years=1)
	year_ago = year_ago.replace(tzinfo=dt.timezone.utc)
	year_ago_str = year_ago.strftime("%Y-%m-%d")
	#print("Year ago utc", year_ago.strftime("%Y-%m-%d"))
	
	# Find each workout json file	
	user_files = []	
	for userfile in sorted(os.listdir(workouts_folder), reverse=True):
		match_user_file = re.search('workout'+'_(....-..-..)_(.+).json',userfile)
		if match_user_file:
			workout_date=match_user_file.group(1)
			if workout_date < year_ago_str:
				break
			workout_id=match_user_file.group(2)
			#print("Found workout file for:",workout_date,workout_id,", in file",userfile)
			user_files.append(userfile)
	print(len(user_files),"user data files to process")
	
	exercises_available = {}
	for user_file in user_files:
		f = open(workouts_folder+"/"+user_file)
		workout_data = json.load(f)
		
		for set_group in workout_data['exercises']:
			if set_group["exercise_type"] == "weight_reps":
				exercises_available[set_group["title"]] = set_group["exercise_template_id"]
				
				filename = user_folder+'/plot_repmax_year_'+re.sub(r'\W+', '', set_group["title"])+'.svg'
				exists = os.path.exists(filename)
				exercises_available[set_group["title"]] = exists
				#print(set_group["title"],exists,filename)

	
	return exercises_available

def generate_plot_rep_max_year(the_exercise, width, height):
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

	
	# work out a year ago
	year_ago = dt.datetime.now() - relativedelta(years=1)
	year_ago = year_ago.replace(tzinfo=dt.timezone.utc)
	year_ago_str = year_ago.strftime("%Y-%m-%d")
	#print("Year ago utc", year_ago.strftime("%Y-%m-%d"))

	# Find each workout json file	
	user_files = []	
	for userfile in sorted(os.listdir(workouts_folder), reverse=True):
		match_user_file = re.search('workout'+'_(....-..-..)_(.+).json',userfile)
		if match_user_file:
			workout_date=match_user_file.group(1)
			if workout_date < year_ago_str:
				break
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
			if set_group["title"] == the_exercise:
				relevant_set_groups.append(set_group)

		if len(relevant_set_groups)>0:
			exercise_to_track_workouts[workout_date] = relevant_set_groups
	print(len(exercise_to_track_workouts.keys()),"relevant user workouts to process")


	# Go through each set group of each workout to find rep maxes for the workout
	exercise_to_track_data = {}
	for workout_date in exercise_to_track_workouts.keys():
		repmax1 = 0
		repmax3 = 0
		repmax5 = 0
		repmax10 = 0
		epley1rm = 0
		brzycki1rm = 0
		
		for set_group in exercise_to_track_workouts[workout_date]:
			for workout_set in set_group['sets']:
				weight = workout_set["weight_kg"]
				reps = workout_set["reps"]
				
				if reps >= 1 and weight > repmax1:
					repmax1 = weight
				if reps >= 3 and weight > repmax3:
					repmax3 = weight
				if reps >= 5 and weight > repmax5:
					repmax5 = weight
				if reps >= 10 and weight > repmax10:
					repmax10 = weight
					
				epley1rm_calc = round( weight * ( 1 + reps / 30.0) , 2)
				brzycki1rm_calc = round( weight * ( (36) / (37 - reps) ) , 2)
				
				if epley1rm_calc > epley1rm and reps <=15:
					epley1rm = epley1rm_calc
				if brzycki1rm_calc > brzycki1rm and reps <=15:
					brzycki1rm = brzycki1rm_calc
		#print("workout:",workout_date,repmax1,repmax3,repmax5,repmax10)
		exercise_to_track_data[workout_date]=(repmax1,repmax3,repmax5,repmax10,epley1rm,brzycki1rm)

	#sys.exit()
	# Now re go through each workout in consecutive order to see first time each rep max was hit
	repmax1_data = []
	repmax1_dates = []
	repmax3_data = []
	repmax3_dates = []
	repmax5_data = []
	repmax5_dates = []
	repmax10_data = []
	repmax10_dates = []
	barchart_dates = []
	barchart_data = []
	epley1rm_data = []
	brzycki1rm_data = []
	
	for workout_key in sorted(exercise_to_track_data.keys()):
		if (len(repmax1_data)==0) or (exercise_to_track_data[workout_key][0]>repmax1_data[-1]):
			repmax1_data.append(exercise_to_track_data[workout_key][0])
			repmax1_dates.append(workout_key)

		if (len(repmax3_data)==0) or (exercise_to_track_data[workout_key][1]>repmax3_data[-1]):
			repmax3_data.append(exercise_to_track_data[workout_key][1])
			repmax3_dates.append(workout_key)

		if (len(repmax5_data)==0) or (exercise_to_track_data[workout_key][2]>repmax5_data[-1]):
			repmax5_data.append(exercise_to_track_data[workout_key][2])
			repmax5_dates.append(workout_key)

		if (len(repmax10_data)==0) or (exercise_to_track_data[workout_key][3]>repmax10_data[-1]):
			repmax10_data.append(exercise_to_track_data[workout_key][3])
			repmax10_dates.append(workout_key)
			
		barchart_dates.append(workout_key)
		barchart_data.append(exercise_to_track_data[workout_key][0])
		epley1rm_data.append(exercise_to_track_data[workout_key][4])
		brzycki1rm_data.append(exercise_to_track_data[workout_key][5])


	#Create dates for each series x axis
	x_repmax1 = [dt.datetime.fromtimestamp(d).date() for d in repmax1_dates]
	x_repmax3 = [dt.datetime.fromtimestamp(d).date() for d in repmax3_dates]
	x_repmax5 = [dt.datetime.fromtimestamp(d).date() for d in repmax5_dates]
	x_repmax10 = [dt.datetime.fromtimestamp(d).date() for d in repmax10_dates]
	x_barchart = [dt.datetime.fromtimestamp(d).date() for d in barchart_dates]


	#Create plot
	plt.style.use('dark_background') # Can just comment out this line if don't want dark style.
	plt.rc('xtick', labelsize=8)
	plt.rc('ytick', labelsize=8)
	plt.rc('legend', fontsize=8) 
	fig, ax1 = plt.subplots()

	ax1.step(x_repmax1, repmax1_data, where='post', label='1RM', alpha=0.8)
	ax1.text(x_repmax1[-1], repmax1_data[-1], str(repmax1_data[-1])+" / "+str(int(repmax1_data[-1]*2.20462262)),fontsize=7,alpha=0.5)
	ax1.step(x_repmax3, repmax3_data, where='post', label='3RM', alpha=0.8)
	ax1.text(x_repmax3[-1], repmax3_data[-1], str(repmax3_data[-1])+" / "+str(int(repmax3_data[-1]*2.20462262)),fontsize=7,alpha=0.5)
	ax1.step(x_repmax5, repmax5_data, where='post', label='5RM', alpha=0.8)
	ax1.text(x_repmax5[-1], repmax5_data[-1], str(repmax5_data[-1])+" / "+str(int(repmax5_data[-1]*2.20462262)),fontsize=7,alpha=0.5)
	ax1.step(x_repmax10, repmax10_data, where='post', label='10RM', alpha=0.8)
	ax1.text(x_repmax10[-1], repmax10_data[-1], str(repmax10_data[-1])+" / "+str(int(repmax10_data[-1]*2.20462262)),fontsize=7,alpha=0.5)
	ax1.bar(x_barchart,barchart_data,alpha=0.5,width=2)
	ax1.plot(x_barchart,epley1rm_data, label='Epley 1rm', alpha=0.8)
	ax1.plot(x_barchart,brzycki1rm_data, label='Brzycki 1rm', alpha=0.8)
	
	# Show scale on both sides
	ax2 = ax1.twinx()
	#ax2.set_ylim(ax1.get_ylim())
	ax2.set_ylim(ax1.get_ylim()[0]*2.20462262,ax1.get_ylim()[1]*2.20462262)

	#Plot formatting
	ax1.legend(loc='lower right')
	plt.title(the_exercise+' Rep Max Record (kg/lb)')
	ax1.set_xlabel("Generated "+str(dt.datetime.now())[:16], fontsize=8)
	fig1 = plt.gcf()
	size=fig1.get_size_inches()
	#fig1.set_size_inches(size[0]*2.5,size[1]*2)
	#fig1.set_size_inches(1600/fig1.dpi,1024/fig.dpi)
	fig.set_size_inches(width/fig1.dpi,height/fig.dpi)
	plt.tight_layout(pad=0.5)
	#plt.show()

	# Write to a folder change png to svg if want that
	export_folder = user_folder
	fig1.savefig(export_folder+'/plot_repmax_year_'+re.sub(r'\W+', '', the_exercise)+'.svg', dpi=100)


