#!/usr/bin/env python3
"""Under the Bar - Plot Body Measures

This file provides a plot of body measures recorded through the Hevy app.

Currently I only use body weight so not entirely sure how well this will work.
"""

import json
import os
import datetime as dt
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# this import is to make pyinstaller import matplotlib properly...
import matplotlib
matplotlib.use("svg")



# INIT
def generate_options_body_measures():
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
	
	measures_file = user_folder + "/body_measurements.json"
	exists = os.path.exists(measures_file)
	if not exists:
		return 404
	
	f = open(measures_file)
	measures_data = json.load(f)
	measures_available = {}
	for measure_group in measures_data["data"]:
		#print(measure_group["date"])
		for measure_key in measure_group.keys():
			#print(measure_key,measure_group[measure_key])
			if (measure_key not in ["date","username","id"]) and measure_group[measure_key] != None:
				filename = user_folder+'/plot_bodymeasures_'+measure_key+'.svg'
				exists = os.path.exists(filename)
				measures_available[measure_key] = exists
	
	return measures_available
	

def generate_plot_body_measures(the_measure, width, height):
	home_folder = str(Path.home())
	utb_folder = home_folder + "/.underthebar"
	session_data = {}
	if os.path.exists(utb_folder+"/session.json"):	
		with open(utb_folder+"/session.json", 'r') as file:
			session_data = json.load(file)
	else:
		return 403
	user_folder = utb_folder + "/user_" + session_data["user-id"]	
	
	measures_file = user_folder + "/body_measurements.json"
	exists = os.path.exists(measures_file)
	if not exists:
		return 404
	
	f = open(measures_file)
	measures_data = json.load(f)
	measure_track_data = []
	measure_track_dates = []
	for measure_group in measures_data["data"]:
		the_data = measure_group[the_measure]
		the_date = measure_group["date"]
		
		if the_data != None:
			measure_track_data.append(the_data)
			measure_track_dates.append(the_date)
		






	#Create dates for each series x axis
	x_dates = [dt.datetime.strptime(d,"%Y-%m-%d").date() for d in measure_track_dates]


	#Create plot
	plt.style.use('dark_background') # Can just comment out this line if don't want dark style.
	plt.rc('xtick', labelsize=8)
	plt.rc('ytick', labelsize=8)
	plt.rc('legend', fontsize=8) 
	fig, ax1 = plt.subplots()
	ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax1.xaxis.get_major_locator()))

	ax1.plot(x_dates, measure_track_data, label=the_measure, alpha=0.8)  #where='post', 
	#ax1.text(x_repmax1[-1], repmax1_data[-1], repmax1_data[-1],fontsize=8,alpha=0.5)
	#ax1.step(x_repmax3, repmax3_data, where='post', label='3RM', alpha=0.8)
	#ax1.text(x_repmax3[-1], repmax3_data[-1], repmax3_data[-1],fontsize=8,alpha=0.5)
	#ax1.step(x_repmax5, repmax5_data, where='post', label='5RM', alpha=0.8)
	#ax1.text(x_repmax5[-1], repmax5_data[-1], repmax5_data[-1],fontsize=8,alpha=0.5)
	#ax1.step(x_repmax10, repmax10_data, where='post', label='10RM', alpha=0.8)
	#ax1.text(x_repmax10[-1], repmax10_data[-1], repmax10_data[-1],fontsize=8,alpha=0.5)
	#ax1.bar(x_barchart,barchart_data,alpha=0.5,width=2)
	
	# Show scale on both sides
	#ax2 = ax1.twinx()
	#ax2.set_ylim(ax1.get_ylim())

	#ax1.set_ylim(ymin=0)
	#Plot formatting
	ax1.legend(loc='lower right')
	plt.title(the_measure+' History')
	ax1.set_xlabel("Generated "+str(dt.datetime.now())[:16], fontsize=8)
	fig1 = plt.gcf()
	#size=fig1.get_size_inches()
	#fig1.set_size_inches(size[0]*2.5,size[1]*2)
	#fig1.set_size_inches(1600/fig1.dpi,1024/fig.dpi)
	fig.set_size_inches(width/fig1.dpi,height/fig.dpi)
	plt.tight_layout(pad=0.5)
	#plt.show()

	# Write to a folder change png to svg if want that
	export_folder = user_folder
	fig1.savefig(export_folder+'/plot_bodymeasures_'+the_measure+'.svg', dpi=100)

def generate_bodyweight_small():
	the_measure = "weight_kg"

	home_folder = str(Path.home())
	utb_folder = home_folder + "/.underthebar"
	session_data = {}
	if os.path.exists(utb_folder+"/session.json"):	
		with open(utb_folder+"/session.json", 'r') as file:
			session_data = json.load(file)
	else:
		return 403
	user_folder = utb_folder + "/user_" + session_data["user-id"]	
	
	measures_file = user_folder + "/body_measurements.json"
	exists = os.path.exists(measures_file)
	if not exists:
		return 404
	
	f = open(measures_file)
	measures_data = json.load(f)
	measure_track_data = []
	measure_track_dates = []
	
	counter = 0
	# just graph the last 20 points
	for measure_group in reversed(measures_data["data"]):
		counter +=1
		if counter> 20:
			break
		the_data = measure_group[the_measure]
		the_date = measure_group["date"]
		
		if the_data != None:
			measure_track_data.append(the_data)
			measure_track_dates.append(the_date)
		






	#Create dates for each series x axis
	x_dates = [dt.datetime.strptime(d,"%Y-%m-%d").date() for d in measure_track_dates]


	#Create plot
	plt.style.use('dark_background') # Can just comment out this line if don't want dark style.
	plt.rc('xtick', labelsize=6)
	plt.rc('ytick', labelsize=6)
	#plt.rc('legend', fontsize=8) 
	
	fig, ax1 = plt.subplots()
	# see this for date formatting https://matplotlib.org/stable/gallery/text_labels_and_annotations/date.html
	#ax1.xaxis.set_major_locator(plt.MaxNLocator(3))
	#ax1.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1,7)))
	ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax1.xaxis.get_major_locator()))

	fig.patch.set_facecolor('black')
	fig.patch.set_alpha(0.0)
	ax1.set_facecolor("black")
	ax1.plot(x_dates, measure_track_data, label=the_measure, alpha=1,color="#2A82DA")  #where='post', 

	#Plot formatting
	#ax1.legend(loc='lower right')
	#plt.title(the_measure+' History')
	#ax1.set_xlabel("Generated "+str(dt.datetime.now())[:16], fontsize=8)
	fig1 = plt.gcf()
	fig.set_size_inches(300/fig1.dpi,200/fig.dpi)
	plt.tight_layout(pad=1)

	# Write to a folder change png to svg if want that
	export_folder = user_folder
	fig1.savefig(export_folder+'/plot_bodyweight_small.svg', dpi=100, facecolor=fig.get_facecolor())#transparent=False)
