#!/usr/bin/env python3
"""Under the Bar - Workouts per month etc

This file provides a plot of workouts per month etc.
"""

import json
import os
import re
import matplotlib.pyplot as plt
import datetime as dt
from dateutil.relativedelta import relativedelta

from pathlib import Path
# INIT



#
# Based on body part reps graph as starting point
#





def generate_options_workouts():
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
	
	# Just a fixed number of options, don't actually need to process files
	exercises_available["per Month"] = os.path.exists(user_folder+'/plot_workouts_permonth'+'.svg')
	exercises_available["per Month (12 months)"] = os.path.exists(user_folder+'/plot_workouts_permonth_12months'+'.svg')
	exercises_available["per Week"] = os.path.exists(user_folder+'/plot_workouts_perweek'+'.svg')
	exercises_available["per Week (12 months)"] = os.path.exists(user_folder+'/plot_workouts_perweek_12months'+'.svg')
	
	return exercises_available
	




def generate_plot_workouts(the_exercise, width, height):
	print("starting generate_plot_workouts ...")

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
	
	#
	# This bit is for limiting to the last 12 months
	#
	timelimit = False
	cal_start_date = None
	weekly = False
	if the_exercise.endswith(" (12 months)"):
		timelimit = True
		# set the start day to first day of the month
		start_date = dt.datetime.now().astimezone()-relativedelta(years=1)
		start_date = start_date - relativedelta(days=(start_date.day-1))		
		cal_start_date = (start_date).strftime("%Y-%m-%d")

	if the_exercise.startswith("per Week"):
		weekly = True
		#set the start day to first day of the week (Sunday)
		start_date = dt.datetime.now().astimezone()-relativedelta(years=1)
		start_date = start_date - relativedelta(days=(start_date.weekday()+1))		
		cal_start_date = (start_date).strftime("%Y-%m-%d")
	


	# Find each workout json file	
	user_files = []	
	for userfile in sorted(os.listdir(workouts_folder), reverse=True):
		match_user_file = re.search('workout'+'_(....-..-..)_(.+).json',userfile)
		if match_user_file:
			workout_date=match_user_file.group(1)
			workout_id=match_user_file.group(2)
			#print("Found workout file for:",workout_date,workout_id,", in file",userfile)
			
			# Break if we're limiting to the last 12 months
			if timelimit and workout_date < cal_start_date:
				break
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
		
		if workout_date in exercise_to_track_workouts.keys():
			exercise_to_track_workouts[workout_date] += 1
		else:
			exercise_to_track_workouts[workout_date] = 1
	print(len(exercise_to_track_workouts.keys()),"relevant user workouts to process")


	# Go through each set group of each workout to find total reps for the workout
	exercise_to_track_data = {}
	exercise_to_track_data_secondary = {}
	exercise_to_track_data_month = {}
	exercise_to_track_data_month_secondary = {}
	for workout_date in exercise_to_track_workouts.keys():
		repcount = 0 + exercise_to_track_workouts[workout_date]
		repcount_secondary = 0
		
		exercise_to_track_data[workout_date]=repcount
		exercise_to_track_data_secondary[workout_date]=repcount_secondary
		
		if weekly:
			# week totals
			workout_week = dt.datetime.fromtimestamp(workout_date, dt.timezone.utc)
			workout_week = (workout_week - dt.timedelta(days=(workout_week.isoweekday()%7))).date()
			if workout_week in exercise_to_track_data_month.keys():
				exercise_to_track_data_month[workout_week] += repcount
				exercise_to_track_data_month_secondary[workout_week] += repcount_secondary
			else:
				exercise_to_track_data_month[workout_week] = repcount
				exercise_to_track_data_month_secondary[workout_week] = repcount_secondary
		else:	
			# month totals
			workout_month = dt.datetime.fromtimestamp(workout_date, dt.timezone.utc)
			workout_month = workout_month.replace(day=1).date()
			if workout_month in exercise_to_track_data_month.keys():
				exercise_to_track_data_month[workout_month] += repcount
				exercise_to_track_data_month_secondary[workout_month] += repcount_secondary
			else:
				exercise_to_track_data_month[workout_month] = repcount
				exercise_to_track_data_month_secondary[workout_month] = repcount_secondary
			#print(exercise_to_track_data_month[workout_month],bodypart_track_data_month[workout_month].total())

	#sys.exit()
	# Now re go through each workout in consecutive order to build cumulative chart
	repcount_data = []
	repcount_dates = []
	barchart_dates = []
	barchart_data = []
	barchart_data_secondary = []
	count_reps = 0
	for workout_key in sorted(exercise_to_track_data.keys()):
		count_reps += exercise_to_track_data[workout_key]
		repcount_data.append(count_reps)
		repcount_dates.append(workout_key)
		barchart_dates.append(workout_key)
		barchart_data.append(exercise_to_track_data[workout_key])
		barchart_data_secondary.append(exercise_to_track_data_secondary[workout_key])


	# do it for the weeks
	monthchart_dates = []
	monthchart_data = []
	monthchart_data_secondary = []
	for month_key in sorted(exercise_to_track_data_month.keys()):
		monthchart_dates.append(month_key)
		monthchart_data.append(exercise_to_track_data_month[month_key])
		monthchart_data_secondary.append(exercise_to_track_data_month_secondary[month_key])


	#Create dates for each series x axis
	x_repcount = [dt.datetime.fromtimestamp(d, dt.timezone.utc).date() for d in repcount_dates]
	x_barchart = [dt.datetime.fromtimestamp(d, dt.timezone.utc).date() for d in barchart_dates]


	#Create plot
	plt.style.use('dark_background') # Can just comment out this line if don't want dark style.
	plt.rc('xtick', labelsize=8)
	plt.rc('ytick', labelsize=8)
	plt.rc('legend', fontsize=8) 
	fig, ax1 = plt.subplots()

	if weekly:
		ax1.bar(monthchart_dates,monthchart_data,alpha=0.5,width=6,align='edge', label='Primary')
	else:
		ax1.bar(monthchart_dates,monthchart_data,alpha=0.5,width=20,align='edge', label='Primary')
	

	#Plot formatting
	ax1.legend(loc='lower right')
	plt.title("Workouts " +the_exercise)


	ax1.set_xlabel("Generated "+str(dt.datetime.now())[:16], fontsize=8)
	ax1.yaxis.tick_right()
	ax1.yaxis.set_ticks_position('both')
	fig1 = plt.gcf()
	size=fig1.get_size_inches()
	#fig1.set_size_inches(size[0]*2.5,size[1]*2)
	#fig1.set_size_inches(1600/fig1.dpi,1024/fig.dpi)
	fig.set_size_inches(width/fig1.dpi,height/fig.dpi)
	plt.tight_layout(pad=0.5)
	

	# Write to a folder change png to svg if want that
	export_folder = user_folder

	filepath = export_folder+'/plot_workouts.svg'
	if the_exercise == "per Month":
		filepath = export_folder+'/plot_workouts_permonth'+'.svg'
	elif the_exercise == "per Month (12 months)":
		filepath = export_folder+'/plot_workouts_permonth_12months'+'.svg'
	elif the_exercise == "per Week":
		filepath = export_folder+'/plot_workouts_perweek'+'.svg'
	elif the_exercise == "per Week (12 months)":
		filepath = export_folder+'/plot_workouts_perweek_12months'+'.svg'
	fig1.savefig(filepath, dpi=100)

	
	plt.close()


