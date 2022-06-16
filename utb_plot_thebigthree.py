#!/usr/bin/env python3
"""Under the Bar - Plot the Big Three

This file provides a plot of personal records for the big three lifts, deadlift, squat, and bench press.

Built this with focus on getting to combined total of 1000LB, so includes a line at 1000LB.

Additionally, has option to include a total based on the estimated 1RM for those lifts.

"""
import json
import os
import re
import matplotlib.pyplot as plt
import datetime as dt

from pathlib import Path

# INIT
def generate_options_big3():
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
	
#	# Find each workout json file	
#	user_files = []	
#	for userfile in sorted(os.listdir(workouts_folder), reverse=True):
#		match_user_file = re.search('workout'+'_(....-..-..)_(.+).json',userfile)
#		if match_user_file:
#			workout_date=match_user_file.group(1)
#			workout_id=match_user_file.group(2)
#			#print("Found workout file for:",workout_date,workout_id,", in file",userfile)
#			user_files.append(userfile)
#	print(len(user_files),"user data files to process")
#	
#	exercises_available = {}
#	for user_file in user_files:
#		f = open(workouts_folder+"/"+user_file)
#		workout_data = json.load(f)
#		
#		for set_group in workout_data['exercises']:
#			if set_group["exercise_type"] == "weight_reps":
#				exercises_available[set_group["title"]] = set_group["exercise_template_id"]
#				
#				filename = user_folder+'/plot_big3_'+re.sub(r'\W+', '', set_group["title"])+'.svg'
#				exists = os.path.exists(filename)
#				exercises_available[set_group["title"]] = exists
#				#print(set_group["title"],exists,filename)

#	
#	return exercises_available

	filename = user_folder+'/plot_big3_alltime.svg'
	filename_brz = user_folder+'/plot_big3_alltime_brz.svg'
	filename_ep = user_folder+'/plot_big3_alltime_ep.svg'
	return {"All Time":os.path.exists(filename),
		"All Time - with Brzycki":os.path.exists(filename_brz),
		"All Time - with Epley":os.path.exists(filename_ep)
		}

def generate_plot_big3(the_option, width, height):
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

	with_brz = False
	with_ep = False
	if the_option == "All Time - with Brzycki":
		with_brz = True
	elif the_option == "All Time - with Epley":
		with_ep = True

	exercises_to_plot = [
		"Bench Press (Barbell)",
		"Squat (Barbell)",
		"Deadlift (Barbell)"
	]

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
			if set_group["title"] in exercises_to_plot:
				relevant_set_groups.append(set_group)

		if len(relevant_set_groups)>0:
			exercise_to_track_workouts[workout_date] = relevant_set_groups
	print(len(exercise_to_track_workouts.keys()),"relevant user workouts to process")


	# Go through each set group of each workout to find rep maxes for the workout
	exercise_to_track_data = {}
	for workout_date in exercise_to_track_workouts.keys():
		bench_epley1rm = 0
		bench_brzycki1rm = 0
		bench_maxweight = 0
		squat_epley1rm = 0
		squat_brzycki1rm = 0
		squat_maxweight = 0
		dead_epley1rm = 0
		dead_brzycki1rm = 0
		dead_maxweight = 0
		
		for set_group in exercise_to_track_workouts[workout_date]:
			for workout_set in set_group['sets']:
				weight = workout_set["weight_kg"]
				reps = workout_set["reps"]
				
				epley1rm_calc = round( weight * ( 1 + reps / 30.0) , 2)
				brzycki1rm_calc = round( weight * ( (36) / (37 - reps) ) , 2)
				
				if set_group['title'] == "Bench Press (Barbell)": 
					if epley1rm_calc > bench_epley1rm and reps <=15:
						bench_epley1rm = epley1rm_calc
					if brzycki1rm_calc > bench_brzycki1rm and reps <=15:
						bench_brzycki1rm = brzycki1rm_calc
					if weight > bench_maxweight:
						bench_maxweight = weight
				elif set_group['title'] == "Squat (Barbell)": 
					if epley1rm_calc > squat_epley1rm and reps <=15:
						squat_epley1rm = epley1rm_calc
					if brzycki1rm_calc > squat_brzycki1rm and reps <=15:
						squat_brzycki1rm = brzycki1rm_calc
					if weight > squat_maxweight:
						squat_maxweight = weight
				elif set_group['title'] == "Deadlift (Barbell)": 
					if epley1rm_calc > dead_epley1rm and reps <=15:
						dead_epley1rm = epley1rm_calc
					if brzycki1rm_calc > dead_brzycki1rm and reps <=15:
						dead_brzycki1rm = brzycki1rm_calc
					if weight > dead_maxweight:
						dead_maxweight = weight

		#print("workout:",workout_date,repmax1,repmax3,repmax5,repmax10)
		exercise_to_track_data[workout_date]=(bench_epley1rm,bench_brzycki1rm,bench_maxweight,squat_epley1rm,squat_brzycki1rm,squat_maxweight,dead_epley1rm,dead_brzycki1rm,dead_maxweight)

	#sys.exit()
	# Now re go through each workout in consecutive order to see first time each rep max was hit
	benchmax_data = []
	benchmax_dates = []
	squatmax_data = []
	squatmax_dates = []
	deadmax_data = []
	deadmax_dates = []
	combo_data = []
	combo_dates = []
	
	bench_brzycki = []
	squat_brzycki = []
	dead_brzycki = []
	combo_brzycki = []
	combo_brzycki_dates = []
	
	bench_epley = []
	squat_epley = []
	dead_epley = []
	combo_epley = []
	combo_epley_dates = []
	
#	repmax3_data = []
#	repmax3_dates = []

#	barchart_dates = []
#	barchart_data = []
	for workout_key in sorted(exercise_to_track_data.keys()):
		newmax = False
		if (len(benchmax_data)==0) or (exercise_to_track_data[workout_key][2]>benchmax_data[-1]):
			benchmax_data.append(exercise_to_track_data[workout_key][2])
			benchmax_dates.append(workout_key)
			newmax = True
			
		if (len(squatmax_data)==0) or (exercise_to_track_data[workout_key][5]>squatmax_data[-1]):
			squatmax_data.append(exercise_to_track_data[workout_key][5])
			squatmax_dates.append(workout_key)
			newmax = True
			
		if (len(deadmax_data)==0) or (exercise_to_track_data[workout_key][8]>deadmax_data[-1]):
			deadmax_data.append(exercise_to_track_data[workout_key][8])
			deadmax_dates.append(workout_key)
			newmax = True
			
		if newmax:
			combo_data.append(benchmax_data[-1]+squatmax_data[-1]+deadmax_data[-1])
			combo_dates.append(workout_key)
		
		# work out brzycki
		newmax = False
		if (len(bench_brzycki)==0) or (exercise_to_track_data[workout_key][1]>bench_brzycki[-1]):
			bench_brzycki.append(exercise_to_track_data[workout_key][1])
			newmax = True	
		if (len(squat_brzycki)==0) or (exercise_to_track_data[workout_key][4]>squat_brzycki[-1]):
			squat_brzycki.append(exercise_to_track_data[workout_key][4])
			newmax = True
		if (len(dead_brzycki)==0) or (exercise_to_track_data[workout_key][7]>dead_brzycki[-1]):
			dead_brzycki.append(exercise_to_track_data[workout_key][7])
			newmax = True
		if newmax:
			combo_brzycki.append(int(bench_brzycki[-1]+squat_brzycki[-1]+dead_brzycki[-1]))
			combo_brzycki_dates.append(workout_key)
		
		# work out epley
		newmax = False
		if (len(bench_epley)==0) or (exercise_to_track_data[workout_key][0]>bench_epley[-1]):
			bench_epley.append(exercise_to_track_data[workout_key][0])
			newmax = True	
		if (len(squat_epley)==0) or (exercise_to_track_data[workout_key][3]>squat_epley[-1]):
			squat_epley.append(exercise_to_track_data[workout_key][3])
			newmax = True
		if (len(dead_epley)==0) or (exercise_to_track_data[workout_key][6]>dead_epley[-1]):
			dead_epley.append(exercise_to_track_data[workout_key][6])
			newmax = True
		if newmax:
			combo_epley.append(int(bench_epley[-1]+squat_epley[-1]+dead_epley[-1]))
			combo_epley_dates.append(workout_key)
			
		#if (len(repmax3_data)==0) or (exercise_to_track_data[workout_key][2]>repmax3_data[-1]):
		#	repmax3_data.append(exercise_to_track_data[workout_key][2])
		#	repmax3_dates.append(workout_key)


			
		#barchart_dates.append(workout_key)
		#barchart_data.append(exercise_to_track_data[workout_key][0])



	#Create dates for each series x axis
	x_benchmax = [dt.datetime.fromtimestamp(d).date() for d in benchmax_dates]
	x_squatmax = [dt.datetime.fromtimestamp(d).date() for d in squatmax_dates]
	x_deadmax = [dt.datetime.fromtimestamp(d).date() for d in deadmax_dates]
	x_combo = [dt.datetime.fromtimestamp(d).date() for d in combo_dates]
	x_brzycki = [dt.datetime.fromtimestamp(d).date() for d in combo_brzycki_dates]
	x_epley = [dt.datetime.fromtimestamp(d).date() for d in combo_epley_dates]
	
	#x_repmax3 = [dt.datetime.fromtimestamp(d).date() for d in repmax3_dates]

	#x_barchart = [dt.datetime.fromtimestamp(d).date() for d in barchart_dates]


	#Create plot
	plt.style.use('dark_background') # Can just comment out this line if don't want dark style.
	plt.rc('xtick', labelsize=8)
	plt.rc('ytick', labelsize=8)
	plt.rc('legend', fontsize=8) 
	fig, ax1 = plt.subplots()

	ax1.step(x_benchmax, benchmax_data, where='post', label='Bench Max Weight', alpha=0.8)
	ax1.text(x_benchmax[-1], benchmax_data[-1], str(benchmax_data[-1])+" / "+str(int(benchmax_data[-1]*2.20462262)),fontsize=6,alpha=0.9)
	ax1.step(x_squatmax, squatmax_data, where='post', label='Squat Max Weight', alpha=0.8)
	ax1.text(x_squatmax[-1], squatmax_data[-1], str(squatmax_data[-1])+" / "+str(int(squatmax_data[-1]*2.20462262)),fontsize=6,alpha=0.9)
	ax1.step(x_deadmax, deadmax_data, where='post', label='Deadlift Max Weight', alpha=0.8)
	ax1.text(x_deadmax[-1], deadmax_data[-1], str(deadmax_data[-1])+" / "+str(int(deadmax_data[-1]*2.20462262)),fontsize=6,alpha=0.9)
	
	ax1.step(x_combo, combo_data, where='post', label='Combined Max Weight', alpha=0.8)
	ax1.text(x_combo[-1], combo_data[-1], str(combo_data[-1])+" / "+str(int(combo_data[-1]*2.20462262)),fontsize=6,alpha=0.9)
	
	if with_brz:
		ax1.step(x_brzycki, combo_brzycki, where='post', label='Brzycki Estimate', alpha=0.8)
		ax1.text(x_brzycki[-1], combo_brzycki[-1], str(combo_brzycki[-1])+" / "+str(int(combo_brzycki[-1]*2.20462262)),fontsize=6,alpha=0.9)
	if with_ep:
		ax1.step(x_epley, combo_epley, where='post', label='Epley Estimate', alpha=0.8)
		ax1.text(x_epley[-1], combo_epley[-1], str(combo_epley[-1])+" / "+str(int(combo_epley[-1]*2.20462262)),fontsize=6,alpha=0.9)
	
	ax1.axhline(453.59, linestyle='--',alpha=0.3)
	#ax1.axvline(x_brzycki[-1], linestyle='--',alpha=0.5)
	#ax1.step(x_repmax3, repmax3_data, where='post', label='Brzycki 1RM', alpha=0.8)
	#ax1.text(x_repmax3[-1], repmax3_data[-1], repmax3_data[-1],fontsize=8,alpha=0.5)
	
	#ax1.bar(x_barchart,barchart_data,alpha=0.5,width=2)
	
	# Show scale on both sides
	ax2 = ax1.twinx()
	ax2.set_ylim(ax1.get_ylim()[0]*2.20462262,ax1.get_ylim()[1]*2.20462262)

	
	#Plot formatting
	ax1.legend(loc='lower right')
	plt.title('The Big Three - All Time Records (kg/lb)')
	if with_brz:
		plt.title('The Big Three - All Time Records with Brzycki Estimate (kg/lb)')
	elif with_ep:
		plt.title('The Big Three - All Time Records with Epley Estimate (kg/lb)')
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
	if with_brz:
		fig1.savefig(export_folder+'/plot_big3_alltime_brz.svg', dpi=100)
	elif with_ep:
		fig1.savefig(export_folder+'/plot_big3_alltime_ep.svg', dpi=100)
	else:
		fig1.savefig(export_folder+'/plot_big3_alltime.svg', dpi=100)


