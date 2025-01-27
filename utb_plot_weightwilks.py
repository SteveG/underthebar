#!/usr/bin/env python3
"""Under the Bar - Plot Max Weight with Wilks

This file provides a plot of max weight per session, plus body weight and wilks score for that lift.

Used Estimated 1RM plot as starting point for developing
"""
import json
import os
import re
import matplotlib.pyplot as plt
import datetime as dt

from pathlib import Path

# INIT
def generate_options_weightwilks():
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
	
	# Find the body_measurements.json file to get the first date we had a body weight recorded
	first_date = None
	if os.path.exists(user_folder +"/body_measurements.json"):
		with open(user_folder +"/body_measurements.json", 'r') as file:
			body_data = json.load(file)
			
			for datum in body_data["data"]:
				if "weight_kg" in datum.keys() and "date" in datum.keys():
					if not first_date:
						first_date = datum["date"]
					elif datum["date"] < first_date:
						first_date = datum["date"]
	else:
		return
	if first_date:
		print("found first date with bodyweight:", first_date)
	else:
		return
	
	# Find each workout json file, discard those created before the first bodyweight measurement.
	user_files = []	
	discarded = []
	for userfile in sorted(os.listdir(workouts_folder), reverse=True):
		match_user_file = re.search('workout'+'_(....-..-..)_(.+).json',userfile)
		if match_user_file:
			workout_date=match_user_file.group(1)
			workout_id=match_user_file.group(2)
			#print("Found workout file for:",workout_date,workout_id,", in file",userfile)
			if workout_date < first_date:
				discarded.append(userfile)
			else:
				user_files.append(userfile)
	print(len(user_files),"user data files to process,", len(discarded),"discarded")
	
	exercises_available = {}
	for user_file in user_files:
		f = open(workouts_folder+"/"+user_file)
		workout_data = json.load(f)
		
		for set_group in workout_data['exercises']:
			if set_group["exercise_type"] == "weight_reps":
				exercises_available[set_group["title"]] = set_group["exercise_template_id"]
				
				filename = user_folder+'/plot_weightwilks_'+re.sub(r'\W+', '', set_group["title"])+'.svg'
				exists = os.path.exists(filename)
				exercises_available[set_group["title"]] = exists
				#print(set_group["title"],exists,filename)

	
	return exercises_available

def generate_plot_weightwilks(the_exercise, width, height):
	print("starting", "generate_plot_weightwilks")
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
	
	# Find the sex to apply correct wilks
	sex = "male"
	try:
		if os.path.exists(user_folder +"/account.json"):
			with open(user_folder +"/account.json", 'r') as file:
				account_data = json.load(file)
				sex = account_data["data"]["sex"]
	except:
		pass
	
	# Find the body_measurements.json file to get the first date we had a body weight recorded
	first_date = None
	bodyweight = {}
	if os.path.exists(user_folder +"/body_measurements.json"):
		with open(user_folder +"/body_measurements.json", 'r') as file:
			body_data = json.load(file)
			
			for datum in body_data["data"]:
				if "weight_kg" in datum.keys() and "date" in datum.keys():
					if not first_date:
						first_date = datum["date"]
					elif datum["date"] < first_date:
						first_date = datum["date"]
					bodyweight[datum["date"]] = datum["weight_kg"]
					#print(datum["date"],datum["weight_kg"])
	else:
		return
	if first_date:
		print("found first date with bodyweight:", first_date)
	else:
		return
	
	

	# Find each workout json file, discard those created before the first bodyweight measurement.
	user_files = []	
	discarded = []
	for userfile in sorted(os.listdir(workouts_folder), reverse=True):
		match_user_file = re.search('workout'+'_(....-..-..)_(.+).json',userfile)
		if match_user_file:
			workout_date=match_user_file.group(1)
			workout_id=match_user_file.group(2)
			#print("Found workout file for:",workout_date,workout_id,", in file",userfile)
			if workout_date < first_date:
				discarded.append(userfile)
			else:
				user_files.append(userfile)
	print(len(user_files),"user data files to process,", len(discarded),"discarded")



	# Process each workout file to get each relevant exercise work out and set group
	exercise_to_track_setgroups = []
	exercise_to_track_dates = []
	exercise_to_track_workouts = {}
	for user_file in user_files:
		f = open(workouts_folder+"/"+user_file)
		workout_data = json.load(f)
		
		#parent_data = {}
		workout_date = workout_data['start_time']
		workout_date = str(dt.datetime.fromtimestamp(workout_date).date())
		#print(workout_date, dt.datetime.fromtimestamp(workout_date).date())
		
		relevant_set_groups = []
		for set_group in workout_data['exercises']:
			if set_group["title"] == the_exercise:
				relevant_set_groups.append(set_group)

		if len(relevant_set_groups)>0:
			exercise_to_track_workouts[workout_date] = relevant_set_groups
	print(len(exercise_to_track_workouts.keys()),"relevant user workouts to process")

	
	# Sorted list of bodyweight measurement dates
	sorted_bodyweight = sorted(bodyweight.keys())
	
	# wilks coefficients
	wc = None
	if sex == "male":
		wc = [-216.0475144,16.2606339,-0.002388645,-0.00113732,7.01863*pow(10,-6),-1.291*pow(10,-8)]
	elif sex == "female":
		wc = [594.31747775582,-27.23842536447,0.82112226871,-0.00930733913,4.731582*pow(10,-5),-9.054*pow(10,-8)]
	
	# Go through each set group of each workout to find rep maxes for the workout
	exercise_to_track_data = {}
	for workout_date in sorted(exercise_to_track_workouts.keys()):
		#epley1rm = 0 # will be the bodyweight
		#brzycki1rm = 0 # will be the wilks
		maxweight = 0
		
		workout_date_bodyweight = 0
		# get the bodyweight at this date, discard earlier bodyweight dates
		#print(len(sorted_bodyweight))
		for x in range (0, len(sorted_bodyweight)):
			#print(x, sorted_bodyweight[x], workout_date)
			if sorted_bodyweight[x] > workout_date:
				workout_date_bodyweight = bodyweight[sorted_bodyweight[x-1]]
				sorted_bodyweight = sorted_bodyweight[x-1:]
				break
			elif x == len(sorted_bodyweight): # at end of the list of bodyweight days so use this one
				workout_date_bodyweight = bodyweight[sorted_bodyweight[x]]
				#print("at the end, using: ", workout_date_bodyweight)
			else:
				#print("foobar", x, sorted_bodyweight[x], workout_date)
				workout_date_bodyweight = bodyweight[sorted_bodyweight[x]]
				
		
		for set_group in exercise_to_track_workouts[workout_date]:
			for workout_set in set_group['sets']:
				weight = workout_set["weight_kg"]
				reps = workout_set["reps"]
				
			
				#epley1rm_calc = round( weight * ( 1 + reps / 30.0) , 2)
				#brzycki1rm_calc = round( weight * ( (36) / (37 - reps) ) , 2)
				
				#if epley1rm_calc > epley1rm and reps <=15:
				#	epley1rm = epley1rm_calc
				#if brzycki1rm_calc > brzycki1rm and reps <=15:
				#	brzycki1rm = brzycki1rm_calc
				if weight > maxweight:
					maxweight = weight
		
		
		bw = workout_date_bodyweight
		wilks = maxweight * 500 / (wc[0]+wc[1]*bw+wc[2]*pow(bw,2)+wc[3]*pow(bw,3)+wc[4]*pow(bw,4)+wc[5]*pow(bw,5))
		

		#print("workout:",workout_date,repmax1,repmax3,repmax5,repmax10)
		exercise_to_track_data[workout_date]=(maxweight,bw,wilks)

	#sys.exit()
	# Now re go through each workout in consecutive order to see first time each rep max was hit
	repmax1_data = []
	repmax1_dates = []
	repmax3_data = []
	repmax3_dates = []

	barchart_dates = []
	barchart_data = []
	for workout_key in sorted(exercise_to_track_data.keys()):
		#print(exercise_to_track_data[workout_key])
		#if (len(repmax1_data)==0) or (exercise_to_track_data[workout_key][1]>repmax1_data[-1]):
		#	repmax1_data.append(exercise_to_track_data[workout_key][1])
		#	repmax1_dates.append(workout_key)
		repmax1_data.append(exercise_to_track_data[workout_key][1])
		repmax1_dates.append(workout_key)

		#if (len(repmax3_data)==0) or (exercise_to_track_data[workout_key][2]>repmax3_data[-1]):
		#	repmax3_data.append(exercise_to_track_data[workout_key][2])
		#	repmax3_dates.append(workout_key)
		repmax3_data.append(exercise_to_track_data[workout_key][2])
		repmax3_dates.append(workout_key)

			
		barchart_dates.append(workout_key)
		barchart_data.append(exercise_to_track_data[workout_key][0])



	#Create dates for each series x axis
	#x_repmax1 = [dt.datetime.fromtimestamp(d).date() for d in repmax1_dates]
	x_repmax1 = [d for d in repmax1_dates]
	x_repmax1 = [dt.datetime.strptime(d,"%Y-%m-%d").date() for d in repmax1_dates]
	
	#x_repmax3 = [dt.datetime.fromtimestamp(d).date() for d in repmax3_dates]
	x_repmax3 = [d for d in repmax3_dates]
	x_repmax3 = x_repmax1

	#x_barchart = [dt.datetime.fromtimestamp(d).date() for d in barchart_dates]
	x_barchart = [d for d in barchart_dates]
	x_barchart = x_repmax1


	#Create plot
	plt.style.use('dark_background') # Can just comment out this line if don't want dark style.
	plt.rc('xtick', labelsize=8)
	plt.rc('ytick', labelsize=8)
	plt.rc('legend', fontsize=8) 
	fig, ax1 = plt.subplots()

	#ax1.step(x_repmax1, repmax1_data, where='post', label='Body Weight', alpha=0.8)
	ax1.plot(x_repmax1, repmax1_data, label='Body Weight', alpha=0.6)
	ax1.text(x_repmax1[-1], repmax1_data[-1], "{:.1f}".format(repmax1_data[-1]),fontsize=7,alpha=0.9)
	#ax1.step(x_repmax3, repmax3_data, where='post', label='Wilks Score', alpha=0.8)
	ax1.plot(x_repmax3, repmax3_data, label='Wilks Score', alpha=0.6)
	ax1.text(x_repmax3[-1], repmax3_data[-1], "{:.1f}".format(repmax3_data[-1]),fontsize=7,alpha=0.9)
	
	ax1.bar(x_barchart,barchart_data,alpha=0.5,width=1)
	
	# Show scale on both sides
	ax2 = ax1.twinx()
	ax2.set_ylim(ax1.get_ylim())

	
	#Plot formatting
	ax1.legend(loc='lower right')
	plt.title(the_exercise+' Max Weight with Wilks')
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
	fig1.savefig(export_folder+'/plot_weightwilks_'+re.sub(r'\W+', '', the_exercise)+'.svg', dpi=100)

if __name__ == "__main__":


	print("trying to plot weight wilks")
	#generate_options_weightwilks()
	generate_plot_weightwilks("Squat (Barbell)", 800,800)


