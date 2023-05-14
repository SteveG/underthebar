#!/usr/bin/env python3
"""Under the Bar - Pull-up / Chin-up Year

This file provides a plot cumulative reps of pull-ups / chin-ups for the year and a comparison to the previous year.
"""
import json
import os
import re
import matplotlib.pyplot as plt
import datetime as dt
from dateutil.relativedelta import relativedelta

from pathlib import Path

# INIT

def generate_options_pullupchinupyear():
	# return every year that had chin-ups or pull-ups completed
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
	
	exercises_to_plot = ["Chin Up",
		"Chin Up (Weighted)",
		"Chin Up (Assisted)",
		"Pull Up (Weighted)",
		"Pull Up",
		"Pull Up (Assisted)"]
	
	# Find each workout json file, group them by year	
	user_files = []	
	user_files_byyear = {}
	for userfile in sorted(os.listdir(workouts_folder), reverse=True):
		match_user_file = re.search('workout'+'_((....)-..-..)_(.+).json',userfile)
		if match_user_file:
			workout_date=match_user_file.group(1)
			workout_year=match_user_file.group(2)
			workout_id=match_user_file.group(3)
			#print("Found workout file for:",workout_date,workout_year,workout_id,", in file",userfile)
			user_files.append(userfile)
			if workout_year not in user_files_byyear.keys():
				user_files_byyear[workout_year] = []
			user_files_byyear[workout_year] += [userfile]
	print(len(user_files_byyear),"years of data files to process")
	
	years_available = {}
	for year in user_files_byyear.keys():
		
		for user_file in user_files_byyear[year]:
			f = open(workouts_folder+"/"+user_file)
			workout_data = json.load(f)
			
			haveyear = False
			for set_group in workout_data['exercises']:
				if set_group["title"] in exercises_to_plot: #["Chin Up (Weighted)", "Pull Up (Weighted)"]:
					#exercises_available[set_group["title"]] = set_group["exercise_template_id"]
					
					filename = user_folder+'/plot_pullupchinupyear_'+year+'.svg'
					exists = os.path.exists(filename)
					years_available[year] = exists
					
					haveyear = True
					break
					#print(set_group["title"],exists,filename)
			if haveyear:
				break
	
	return years_available


def generate_plot_pullupchinupyear(year, width, height):
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

#	exercises_to_plot = {
#		"023943F1":"Chin Up (Weighted)",
#		"729237D1":"Pull Up (Weighted)"
#	}
	exercises_to_plot = ["Chin Up",
		"Chin Up (Weighted)",
		"Chin Up (Assisted)",
		"Pull Up (Weighted)",
		"Pull Up",
		"Pull Up (Assisted)"]

	plot_year = dt.datetime.now().year # override this to specify a year
	plot_year = int(year)
	#plot_year = 2021
	plot_year_start = dt.datetime(plot_year,1,1,0,0,0)
	plot_year_start_timestamp = plot_year_start.replace(tzinfo=dt.timezone.utc).timestamp()
	plot_year_end = dt.datetime(plot_year,12,31,23,59,59)
	plot_year_end_timestamp = plot_year_end.replace(tzinfo=dt.timezone.utc).timestamp()

	plot_prev_year = plot_year - 1 # override this to specify a year
	plot_prev_year_start = dt.datetime(plot_prev_year,1,1,0,0,0)
	plot_prev_year_start_timestamp = plot_prev_year_start.replace(tzinfo=dt.timezone.utc).timestamp()
	plot_prev_year_end = dt.datetime(plot_prev_year,12,31,23,59,59)
	plot_prev_year_end_timestamp = plot_prev_year_end.replace(tzinfo=dt.timezone.utc).timestamp()


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
		#f = open("./hevy_data/user_"+their_user_id+"/"+user_file)
		workout_data = json.load(f)
		
		#parent_data = {}
		workout_date = workout_data['start_time']
		
		relevant_set_groups = []
		for set_group in workout_data['exercises']:
			#if set_group["exercise_template_id"] in exercises_to_plot.keys():
			if set_group["title"] in exercises_to_plot:
				relevant_set_groups.append(set_group)
			
		if len(relevant_set_groups)>0:
			exercise_to_track_workouts[workout_date] = relevant_set_groups
	print(len(exercise_to_track_workouts.keys()),"relevant user workouts to process")


	# Go through each set group of each workout to find total reps for the workout
	exercise_to_track_data = {}
	for workout_date in exercise_to_track_workouts.keys():
		repcount = 0
		
		for set_group in exercise_to_track_workouts[workout_date]:
			for workout_set in set_group['sets']:
				reps = workout_set["reps"]
				
				repcount += reps
		#print("workout:",workout_date,repmax1,repmax3,repmax5,repmax10)
		exercise_to_track_data[workout_date]=repcount

	#sys.exit()

	# Now re go through each workout in consecutive order to build cumulative chart

	repcount_data = []
	repcount_dates = []
	repcount_prev_data = []
	repcount_prev_dates = []

	barchart_dates = []
	barchart_data = []
	barchart_prev_dates = []
	barchart_prev_data = []

	count_reps = 0
	count_prev_reps = 0
	for workout_key in sorted(exercise_to_track_data.keys()):
		if workout_key >= plot_year_start_timestamp and workout_key <= plot_year_end_timestamp:
			count_reps += exercise_to_track_data[workout_key]
			repcount_data.append(count_reps)
			repcount_dates.append(workout_key)
			barchart_dates.append(workout_key)
			barchart_data.append(exercise_to_track_data[workout_key])
		elif workout_key >= plot_prev_year_start_timestamp and workout_key <= plot_prev_year_end_timestamp:
			count_prev_reps += exercise_to_track_data[workout_key]
			repcount_prev_data.append(count_prev_reps)
			repcount_prev_dates.append(workout_key)
			barchart_prev_dates.append(workout_key)
			barchart_prev_data.append(exercise_to_track_data[workout_key])



	#Create dates for each series x axis
	x_repcount = [dt.datetime.fromtimestamp(d, dt.timezone.utc).date() for d in repcount_dates]
	x_barchart = [dt.datetime.fromtimestamp(d, dt.timezone.utc).date() for d in barchart_dates]

	x_prev_repcount = [(dt.datetime.fromtimestamp(d, dt.timezone.utc)+relativedelta(years=1)).date() for d in repcount_prev_dates]
	x_prev_barchart = [(dt.datetime.fromtimestamp(d, dt.timezone.utc)+relativedelta(years=1)).date() for d in barchart_prev_dates]


	#Create plot
	plt.style.use('dark_background') # Can just comment out this line if don't want dark style.
	plt.rc('xtick', labelsize=8)
	plt.rc('ytick', labelsize=8)
	plt.rc('legend', fontsize=8) 
	fig, ax1 = plt.subplots()
	ax2 = ax1.twinx()

	ax1.plot(x_repcount, repcount_data, label=str(plot_year)+' Reps', alpha=0.8)
	ax1.text(x_repcount[-1], repcount_data[-1], repcount_data[-1],fontsize=7,alpha=0.8)

	ax1.plot(x_prev_repcount, repcount_prev_data, label=str(plot_prev_year)+' Reps', alpha=0.8)
	if len(repcount_prev_data)>0:
		ax1.text(x_prev_repcount[-1], repcount_prev_data[-1], repcount_prev_data[-1],fontsize=7,alpha=0.8)
	
	ax2.bar(x_barchart,barchart_data,alpha=0.4,width=2)
	ax2.bar(x_prev_barchart,barchart_prev_data,alpha=0.2,width=2)

	#Plot formatting
	ax1.legend(loc='lower right')
	plt.title('Pull-Up and Chin-up Combined Reps ('+str(plot_year)+')')
	ax1.set_xlabel("Generated "+str(dt.datetime.now())[:16], fontsize=8)
	fig1 = plt.gcf()
	size=fig1.get_size_inches()
	#fig1.set_size_inches(size[0]*2.5,size[1]*2)
	#fig1.set_size_inches(1600/fig1.dpi,1024/fig.dpi)
	fig.set_size_inches(width/fig1.dpi,height/fig.dpi)
	plt.tight_layout(pad=0.5)
	#plt.show()

	# Write to a folder change png to svg if want that
	#export_folder = "./hevy_export/user_"+their_user_id
	#fig1.savefig(export_folder+'/plot_pullupchinup_comb_'+str(plot_year)+'.png', dpi=100)

	# Write to a folder change png to svg if want that
	export_folder = user_folder
	fig1.savefig(export_folder+'/plot_pullupchinupyear_'+year+'.svg', dpi=100)
