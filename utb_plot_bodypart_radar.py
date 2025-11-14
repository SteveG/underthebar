from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsTextItem
from PySide6.QtCharts import QChart, QChartView, QPolarChart, QLineSeries, QAreaSeries, QValueAxis
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen

from pathlib import Path
import os
import json
import re
import datetime as dt
from dateutil.relativedelta import relativedelta
import numpy as np



def generate_options_bodypart_radar():
	options = {
		"All - 1 Month":False,
		"All - 3 Months":False,
		"All - 6 Months":False,
		"All - 12 Months":False,
		"All - 24 Months":False,
		"Compare Sets - 1 Month":False,
		"Compare Sets - 3 Months":False,
		"Compare Sets - 6 Months":False,
		"Compare Sets - 12 Months":False,
		"Compare Reps - 1 Month":False,
		"Compare Reps - 3 Months":False,
		"Compare Reps - 6 Months":False,
		"Compare Reps - 12 Months":False,
		"Compare Volume - 1 Month":False,
		"Compare Volume - 3 Months":False,
		"Compare Volume - 6 Months":False,
		"Compare Volume - 12 Months":False,
	}
	return options
	
	
class UTBPlotBodyPartRadar(QChartView):
	def __init__(self, requestedOption):
		super().__init__()
		self.labels = []
		if requestedOption== "All - 1 Month":
			self.draw_months_all(1)
		elif requestedOption== "All - 3 Months":
			self.draw_months_all(3)
		elif requestedOption== "All - 6 Months":
			self.draw_months_all(6)
		elif requestedOption== "All - 12 Months":
			self.draw_months_all(12)
		elif requestedOption== "All - 24 Months":
			self.draw_months_all(24)
		elif requestedOption== "Compare Sets - 1 Month":
			self.draw_months_comparision(1, "Sets")
		elif requestedOption== "Compare Sets - 3 Months":
			self.draw_months_comparision(3, "Sets")
		elif requestedOption== "Compare Sets - 6 Months":
			self.draw_months_comparision(6, "Sets")
		elif requestedOption== "Compare Sets - 12 Months":
			self.draw_months_comparision(12, "Sets")
		elif requestedOption== "Compare Reps - 1 Month":
			self.draw_months_comparision(1, "Reps")
		elif requestedOption== "Compare Reps - 3 Months":
			self.draw_months_comparision(3, "Reps")
		elif requestedOption== "Compare Reps - 6 Months":
			self.draw_months_comparision(6, "Reps")
		elif requestedOption== "Compare Reps - 12 Months":
			self.draw_months_comparision(12, "Reps")
		elif requestedOption== "Compare Volume - 1 Month":
			self.draw_months_comparision(1, "Volume")
		elif requestedOption== "Compare Volume - 3 Months":
			self.draw_months_comparision(3, "Volume")
		elif requestedOption== "Compare Volume - 6 Months":
			self.draw_months_comparision(6, "Volume")
		elif requestedOption== "Compare Volume - 12 Months":
			self.draw_months_comparision(12, "Volume")
		
		self.chart().scene().changed.connect(self.update_label_positions)
		return
		
		# Below is messing around stuff
		chart = QPolarChart()
		#chart.setBackgroundBrush(QBrush(QColor("black")))
		self.setChart(chart)
		chart.legend().setAlignment(Qt.AlignRight)
		chart.setTitle("My Polar Chart")
		#chart.setTheme(QChart.ChartThemeBlueIcy)

		print("create axis")
		angular_axis = QValueAxis()
		angular_axis.setRange(0,6)
		angular_axis.setTitleText(" ")#Angle (degrees)")
		angular_axis.setLabelFormat(" ")
		angular_axis.setLineVisible(False)
		angular_axis.setGridLineVisible(True)
		angular_axis.setTickCount(7)
		chart.addAxis(angular_axis, QPolarChart.PolarOrientationAngular)

		radial_axis = QValueAxis()
		radial_axis.setRange(0,10)
		radial_axis.setTitleText(" ")
		radial_axis.setLabelFormat(" ")
		radial_axis.setLineVisible(False)
		radial_axis.setGridLineVisible(False)
		chart.addAxis(radial_axis, QPolarChart.PolarOrientationRadial)



		print("create line series")
		series = QLineSeries()
		series.setName("April")
		series.append(QPointF(0,7))
		series.append(QPointF(1,8))
		series.append(QPointF(2,7))
		series.append(QPointF(3,8))
		series.append(QPointF(4,7))
		series.append(QPointF(5,8))
		series.append(QPointF(6,7))
		
		series2 = QLineSeries()
		series2.setName("April")
		series2.append(QPointF(0,0))
		#series2.append(QPointF(1,0))
		#series2.append(QPointF(2,0))
		#series2.append(QPointF(3,0))
		#series2.append(QPointF(4,0))
		#series2.append(QPointF(5,0))
		series2.append(QPointF(6,0))

		chart.addSeries(series)
		chart.addSeries(series2)
		areaSeries = QAreaSeries(series,series2)
		areaSeries.setPen(QPen(QColor("blue"), 2))
		#color = areaSeries.pen().color()
		#color.setAlpha(210)
		#areaSeries.setPen(QPen(color,2))
		#areaSeries.setBrush(QBrush(QColor(0,0,255,90)))
		color = areaSeries.brush().color()
		color.setAlpha(20)
		areaSeries.setBrush(QBrush(color))


		chart.addSeries(areaSeries)
		series.attachAxis(angular_axis)
		series.attachAxis(radial_axis)
		


		#create 10 lines
		for x in range(1,11):
			print(x)
			series = QLineSeries()
			series.setName("Fish "+str(x))
			series.append(0,x)
			series.append(1,x)
			series.append(2,x)
			series.append(3,x)
			series.append(4,x)
			series.append(5,x)
			series.append(6,x)
			series.setColor(QColor("darkgray"))

			chart.addSeries(series)
			
			series.attachAxis(angular_axis)
			series.attachAxis(radial_axis)
		#	serieslist.append(series)
			if chart.legend().markers(series):
				chart.legend().markers(series)[0].setVisible(False)
				
		self.reference_series = series
		self.labels = []
		self.labels.append((QPointF(0,10),QGraphicsTextItem("Toad", parent=self.chart())))
		self.labels.append((QPointF(1,10),QGraphicsTextItem("Toadstool", parent=self.chart())))
		self.labels.append((QPointF(2,10),QGraphicsTextItem("Toad", parent=self.chart())))
		self.labels.append((QPointF(3,10),QGraphicsTextItem("Toadstool", parent=self.chart())))
		self.labels.append((QPointF(4,10),QGraphicsTextItem("Toad", parent=self.chart())))
		self.labels.append((QPointF(5,10),QGraphicsTextItem("Toadstool", parent=self.chart())))
		
		chart.scene().changed.connect(self.update_label_positions)
	

	
	def load_data(self, start_date, end_date):
		timelimit = True
		if start_date == None:
			timelimit = False
	
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
		
		
		
		
		
		
#		the_exercise = " (12 months)"
		#
		# This bit is for limiting to the last 12 months
		#
#		timelimit = False
#		cal_start_date = None
#		weekly = False
#		if the_exercise.endswith(" (12 months)"):
#			timelimit = True
#			cal_start_date = (dt.datetime.now().astimezone()-relativedelta(years=1)).strftime("%Y-%m-%d")
#			the_exercise = the_exercise[:-12]
#		if the_exercise.endswith(" (weekly)"):
#			weekly = True
#			timelimit = True
#			cal_start_date = (dt.datetime.now().astimezone()-relativedelta(years=1)).strftime("%Y-%m-%d")
#			the_exercise = the_exercise[:-9]
#		if the_exercise.endswith(" (weekly prop)"):
#			weekly = True
#			timelimit = True
#			cal_start_date = (dt.datetime.now().astimezone()-relativedelta(years=1)).strftime("%Y-%m-%d")	

		# Find each workout json file	
		user_files = []	
		for userfile in sorted(os.listdir(workouts_folder), reverse=True):
			match_user_file = re.search('workout'+'_(....-..-..)_(.+).json',userfile)
			if match_user_file:
				workout_date=match_user_file.group(1)
				workout_id=match_user_file.group(2)
				#print("Found workout file for:",workout_date,workout_id,", in file",userfile)
				if workout_date <= end_date:
					user_files.append(userfile)
				
				# Break if we're limiting to the last 12 months
				if timelimit and workout_date < start_date:
					break
		print(len(user_files),"user data files to process")


		# Process each workout file to get each relevant exercise work out and set group
		bodypart_reps = {}
		bodypart_sets = {}
		bodypart_volume = {}
		
		#exercise_to_track_setgroups = []
		#exercise_to_track_dates = []
		#exercise_to_track_workouts = {}
		for user_file in user_files:
			f = open(workouts_folder+"/"+user_file)
			workout_data = json.load(f)
			
			#parent_data = {}
			workout_date = workout_data['start_time']
			
			relevant_set_groups = []
			for set_group in workout_data['exercises']:
				#if set_group["muscle_group"] == the_exercise:
				#	relevant_set_groups.append(set_group)
				#elif the_exercise in set_group["other_muscles"] or the_exercise[0:7]=="--All--":
				#	relevant_set_groups.append(set_group)
				set_group_sets = len(set_group["sets"])
				set_group_reps = 0
				set_group_volume = 0
				for ex_set in set_group["sets"]:
					if ex_set["reps"] != None:
						set_group_reps += ex_set["reps"]
						
						# If one of the special bodyweight exercises we want to use bodyweight added to weight lifted, e.g. chinups
						add_bodyweight = 0
						if set_group["title"] in special_bodyweight:
							use_date = int(dt.datetime.fromtimestamp(workout_date, dt.timezone.utc).strftime("%Y%m%d"))
							prev_dates = bodyweight_dates[bodyweight_dates < use_date]
							if len(prev_dates)>0:
								add_bodyweight = bodyweight_data[int(prev_dates.max())]
						
						if ex_set["weight_kg"] != None:
							set_group_volume += ex_set["reps"]*(ex_set["weight_kg"]+add_bodyweight)
						elif add_bodyweight != 0: #case that weight is none but still is a special bodyweight exercise
							set_group_volume += ex_set["reps"]*add_bodyweight
				
				if set_group["muscle_group"] in bodypart_sets.keys():
					bodypart_sets[set_group["muscle_group"]] += set_group_sets
					bodypart_reps[set_group["muscle_group"]] += set_group_reps
					bodypart_volume[set_group["muscle_group"]] += set_group_volume
					
					for other_bodypart in set_group["other_muscles"]:
						if other_bodypart in bodypart_sets.keys():
							bodypart_sets[other_bodypart] += float(set_group_sets)/2
							bodypart_reps[other_bodypart] += float(set_group_reps)/2
							bodypart_volume[other_bodypart] += float(set_group_volume)/2
						else:
							bodypart_sets[other_bodypart] = float(set_group_sets)/2
							bodypart_reps[other_bodypart] = float(set_group_reps)/2
							bodypart_volume[other_bodypart] = float(set_group_volume)/2
					
				else:
					bodypart_sets[set_group["muscle_group"]] = float(set_group_sets)
					bodypart_reps[set_group["muscle_group"]] = float(set_group_reps)
					bodypart_volume[set_group["muscle_group"]] = float(set_group_volume)
					
					for other_bodypart in set_group["other_muscles"]:
						if other_bodypart in bodypart_sets.keys():
							bodypart_sets[other_bodypart] += float(set_group_sets)/2
							bodypart_reps[other_bodypart] += float(set_group_reps)/2
							bodypart_volume[other_bodypart] += float(set_group_volume)/2
						else:
							bodypart_sets[other_bodypart] = float(set_group_sets)/2
							bodypart_reps[other_bodypart] = float(set_group_reps)/2
							bodypart_volume[other_bodypart] = float(set_group_volume)/2
		bodypart_sets.pop("cardio", None)
		bodypart_sets.pop("full_body", None)
		bodypart_reps.pop("cardio", None)
		bodypart_reps.pop("full_body", None)
		bodypart_volume.pop("cardio", None)
		bodypart_volume.pop("full_body", None)
		
		
		print(len(sorted(bodypart_sets.keys())), "bodyparts")
		sorted_parts = sorted(bodypart_sets.keys())
		num_parts = len(sorted_parts)
				
		#print(bodypart_sets)
		#print(bodypart_reps)
		#print(bodypart_volume)
		
		return bodypart_sets, bodypart_reps, bodypart_volume
		#	if len(relevant_set_groups)>0:
		#		exercise_to_track_workouts[workout_date] = relevant_set_groups
		#print(len(exercise_to_track_workouts.keys()),"relevant user workouts to process")

	# Picked these from Color Brewer *shrugs*
	# 166, 206, 227
	# 31, 120, 180
	# 178, 223, 138
	def draw_months_comparision(self, numberofmonths, setsrepsorvolume):
		print("Create Months Comparison Chart:", setsrepsorvolume)
		cal_start_date1 = (dt.datetime.now().astimezone()-relativedelta(months=numberofmonths)).strftime("%Y-%m-%d")
		cal_end_date1 = (dt.datetime.now().astimezone()).strftime("%Y-%m-%d")
		bodypart_sets1, bodypart_reps1, bodypart_volume1 = self.load_data(cal_start_date1, cal_end_date1)
		sorted_parts1 = sorted(bodypart_sets1.keys())
		num_parts1 = len(sorted_parts1)
		
		cal_start_date2 = (dt.datetime.now().astimezone()-relativedelta(months=numberofmonths*2, days=1)).strftime("%Y-%m-%d")
		cal_end_date2 = (dt.datetime.now().astimezone()-relativedelta(months=numberofmonths, days=1)).strftime("%Y-%m-%d")
		bodypart_sets2, bodypart_reps2, bodypart_volume2 = self.load_data(cal_start_date2, cal_end_date2)
		sorted_parts2 = sorted(bodypart_sets2.keys())
		num_parts2 = len(sorted_parts2)
		
		# check for bodypart mismatch
		for part in sorted_parts1:
			if part not in sorted_parts2:
				bodypart_sets2[part] = 0
				bodypart_reps2[part] = 0
				bodypart_volume2[part] = 0
		for part in sorted_parts2:
			if part not in sorted_parts1:
				bodypart_sets1[part] = 0
				bodypart_reps1[part] = 0
				bodypart_volume1[part] = 0
		sorted_parts = sorted(bodypart_sets1.keys())
		num_parts = len(sorted_parts1)
		
		
		chart = QPolarChart()
		chart.setBackgroundBrush(QBrush(QColor("black")))
		self.setChart(chart)
		chart.legend().setAlignment(Qt.AlignRight)
		chart.setTitleBrush(QBrush(QColor("white")))
		chart.setTitle("Body Part "+setsrepsorvolume+" "+str(numberofmonths)+ " Month Comparison")
		#chart.setTheme(QChart.ChartThemeBlueIcy)

		print("create axis")
		angular_axis = QValueAxis()
		angular_axis.setRange(0,num_parts)
		angular_axis.setTitleText(" ")#Angle (degrees)")
		angular_axis.setLabelFormat(" ")
		angular_axis.setLineVisible(False)
		angular_axis.setGridLineVisible(True)
		angular_axis.setTickCount(num_parts+1)
		chart.addAxis(angular_axis, QPolarChart.PolarOrientationAngular)

		radial_axis = QValueAxis()
		radial_axis.setRange(0,10)
		radial_axis.setTitleText(" ")
		radial_axis.setLabelFormat(" ")
		radial_axis.setLineVisible(False)
		radial_axis.setGridLineVisible(False)
		chart.addAxis(radial_axis, QPolarChart.PolarOrientationRadial)
		
		#create 10 lines and labels
		self.labels = []
		for x in range(1,6):
			series = QLineSeries()
			series.setName("Fish "+str(x))
			
			series.setColor(QColor("darkgray"))
			for y in range(0, num_parts):
			
			
				series.append(y,x*2)
				self.labels.append((QPointF(y,10),QGraphicsTextItem(sorted_parts[y], parent=self.chart())))
			series.append(num_parts,x*2)

			chart.addSeries(series)
			
			series.attachAxis(angular_axis)
			series.attachAxis(radial_axis)
			self.reference_series = series
		#	serieslist.append(series)
			if chart.legend().markers(series):
				chart.legend().markers(series)[0].setVisible(False)
				
		bottomseries = QLineSeries()
		bottomseries.append(0,0)
		bottomseries.append(1,0)
		
		if setsrepsorvolume == "Sets":
			max_sets = max(max(bodypart_sets1.values()),max(bodypart_sets2.values()))
			series = QLineSeries()
			series.setName("Now")
			series.setPen(QPen(QColor(166,206,227), 2))
			for x in range(0, num_parts):
				series.append(x,bodypart_sets1[sorted_parts[x]]/max_sets*10)
			series.append(num_parts,bodypart_sets1[sorted_parts[0]]/max_sets*10)
			chart.addSeries(series)
			series.attachAxis(angular_axis)
			series.attachAxis(radial_axis)
			
			series1 = QLineSeries()
			series1.setName("Before")
			series1.setPen(QPen(QColor(31,120,180), 2))
			for x in range(0, num_parts):
				series1.append(x,bodypart_sets2[sorted_parts[x]]/max_sets*10)
			series1.append(num_parts,bodypart_sets2[sorted_parts[0]]/max_sets*10)
			chart.addSeries(series1)
			series1.attachAxis(angular_axis)
			series1.attachAxis(radial_axis)
			
			# new stuff
			chart.addSeries(bottomseries)
			chart.legend().markers(bottomseries)[0].setVisible(False)
			bottomseries.attachAxis(angular_axis)
			bottomseries.attachAxis(radial_axis)
			
			areaSeries = QAreaSeries(series,bottomseries)
			areaSeries.setPen(QPen(QColor(166,206,227), 2))
			areaSeries.setBrush(QBrush(QColor(166,206,227,50)))
			chart.addSeries(areaSeries)
			chart.legend().markers(areaSeries)[0].setVisible(False)
			
			areaSeries1 = QAreaSeries(series1,bottomseries)
			areaSeries1.setPen(QPen(QColor(31,120,180), 2))
			areaSeries1.setBrush(QBrush(QColor(31,120,180,50)))
			chart.addSeries(areaSeries1)
			chart.legend().markers(areaSeries1)[0].setVisible(False)
			
			#Dunno why this is necessary
			if max_sets == max(bodypart_sets1.values()): 
				areaSeries1.attachAxis(angular_axis)
				areaSeries1.attachAxis(radial_axis)
			else:
				areaSeries.attachAxis(angular_axis)
				areaSeries.attachAxis(radial_axis)
		
		elif setsrepsorvolume == "Reps":
			max_reps = max(max(bodypart_reps1.values()),max(bodypart_reps2.values()))
			series = QLineSeries()
			series.setName("Now")
			series.setPen(QPen(QColor(166,206,227), 2))
			for x in range(0, num_parts):
				series.append(x,bodypart_reps1[sorted_parts[x]]/max_reps*10)
			series.append(num_parts,bodypart_reps1[sorted_parts[0]]/max_reps*10)
			chart.addSeries(series)
			series.attachAxis(angular_axis)
			series.attachAxis(radial_axis)
			
			series1 = QLineSeries()
			series1.setName("Before")
			series1.setPen(QPen(QColor(31,120,180), 2))
			for x in range(0, num_parts):
				series1.append(x,bodypart_reps2[sorted_parts[x]]/max_reps*10)
			series1.append(num_parts,bodypart_reps2[sorted_parts[0]]/max_reps*10)
			chart.addSeries(series1)
			series1.attachAxis(angular_axis)
			series1.attachAxis(radial_axis)
			
			# new stuff
			chart.addSeries(bottomseries)
			chart.legend().markers(bottomseries)[0].setVisible(False)
			bottomseries.attachAxis(angular_axis)
			bottomseries.attachAxis(radial_axis)
			
			areaSeries = QAreaSeries(series,bottomseries)
			areaSeries.setPen(QPen(QColor(166,206,227), 2))
			areaSeries.setBrush(QBrush(QColor(166,206,227,50)))
			chart.addSeries(areaSeries)
			chart.legend().markers(areaSeries)[0].setVisible(False)
			
			areaSeries1 = QAreaSeries(series1,bottomseries)
			areaSeries1.setPen(QPen(QColor(31,120,180), 2))
			areaSeries1.setBrush(QBrush(QColor(31,120,180,50)))
			chart.addSeries(areaSeries1)
			chart.legend().markers(areaSeries1)[0].setVisible(False)
			
			#Dunno why this is necessary
			if max_reps == max(bodypart_reps1.values()): 
				areaSeries1.attachAxis(angular_axis)
				areaSeries1.attachAxis(radial_axis)
			else:
				areaSeries.attachAxis(angular_axis)
				areaSeries.attachAxis(radial_axis)
				
				
		
		elif setsrepsorvolume == "Volume":
			max_volume = max(max(bodypart_volume1.values()),max(bodypart_volume2.values()))
			series = QLineSeries()
			series.setName("Now")
			series.setPen(QPen(QColor(166,206,227), 2))
			for x in range(0, num_parts):
				series.append(x,bodypart_volume1[sorted_parts[x]]/max_volume*10)
			series.append(num_parts,bodypart_volume1[sorted_parts[0]]/max_volume*10)
			chart.addSeries(series)
			series.attachAxis(angular_axis)
			series.attachAxis(radial_axis)	
			
			series1 = QLineSeries()
			series1.setName("Before")
			series1.setPen(QPen(QColor(31,120,180), 2))
			for x in range(0, num_parts):
				series1.append(x,bodypart_volume2[sorted_parts[x]]/max_volume*10)
			series1.append(num_parts,bodypart_volume2[sorted_parts[0]]/max_volume*10)
			chart.addSeries(series1)
			series1.attachAxis(angular_axis)
			series1.attachAxis(radial_axis)
			
			# new stuff
			chart.addSeries(bottomseries)
			chart.legend().markers(bottomseries)[0].setVisible(False)
			bottomseries.attachAxis(angular_axis)
			bottomseries.attachAxis(radial_axis)
			
			areaSeries = QAreaSeries(series,bottomseries)
			areaSeries.setPen(QPen(QColor(166,206,227), 2))
			areaSeries.setBrush(QBrush(QColor(166,206,227,50)))
			chart.addSeries(areaSeries)
			chart.legend().markers(areaSeries)[0].setVisible(False)
			
			areaSeries1 = QAreaSeries(series1,bottomseries)
			areaSeries1.setPen(QPen(QColor(31,120,180), 2))
			areaSeries1.setBrush(QBrush(QColor(31,120,180,50)))
			chart.addSeries(areaSeries1)
			chart.legend().markers(areaSeries1)[0].setVisible(False)
			
			#Dunno why this is necessary
			if max_volume == max(bodypart_volume1.values()): 
				areaSeries1.attachAxis(angular_axis)
				areaSeries1.attachAxis(radial_axis)
			else:
				areaSeries.attachAxis(angular_axis)
				areaSeries.attachAxis(radial_axis)
		

	def draw_months_all(self, numberofmonths):
	
		cal_start_date = (dt.datetime.now().astimezone()-relativedelta(months=numberofmonths)).strftime("%Y-%m-%d")
		cal_end_date = (dt.datetime.now().astimezone()).strftime("%Y-%m-%d")
		print("Drawing Graph:", cal_start_date, cal_end_date)
		bodypart_sets, bodypart_reps, bodypart_volume = self.load_data(cal_start_date, cal_end_date)
		sorted_parts = sorted(bodypart_sets.keys())
		num_parts = len(sorted_parts)
	
		chart = QPolarChart()
		chart.setBackgroundBrush(QBrush(QColor("black")))
		self.setChart(chart)
		chart.legend().setAlignment(Qt.AlignRight)
		chart.setTitleBrush(QBrush(QColor("white")))
		chart.setTitle("Body Part Sets / Reps / Volume Over "+str(numberofmonths)+" Months")
		#chart.setTheme(QChart.ChartThemeBlueIcy)

		print("create axis")
		angular_axis = QValueAxis()
		angular_axis.setRange(0,num_parts)
		angular_axis.setTitleText(" ")#Angle (degrees)")
		angular_axis.setLabelFormat(" ")
		angular_axis.setLineVisible(False)
		angular_axis.setGridLineVisible(True)
		angular_axis.setTickCount(num_parts+1)
		chart.addAxis(angular_axis, QPolarChart.PolarOrientationAngular)

		radial_axis = QValueAxis()
		radial_axis.setRange(0,10)
		radial_axis.setTitleText(" ")
		radial_axis.setLabelFormat(" ")
		radial_axis.setLineVisible(False)
		radial_axis.setGridLineVisible(False)
		chart.addAxis(radial_axis, QPolarChart.PolarOrientationRadial)

		#create 10 lines and labels
		self.labels = []
		for x in range(1,6):
			series = QLineSeries()
			series.setName("Fish "+str(x))
			
			series.setColor(QColor("darkgray"))
			for y in range(0, num_parts):
			
			
				series.append(y,x*2)
				self.labels.append((QPointF(y,10),QGraphicsTextItem(sorted_parts[y], parent=self.chart())))
			series.append(num_parts,x*2)

			chart.addSeries(series)
			
			series.attachAxis(angular_axis)
			series.attachAxis(radial_axis)
			self.reference_series = series
		#	serieslist.append(series)
			if chart.legend().markers(series):
				chart.legend().markers(series)[0].setVisible(False)
		
		max_sets = max(bodypart_sets.values())
		series = QLineSeries()
		series.setName("Sets")
		series.setPen(QPen(QColor(166,206,227), 2))
		for x in range(0, num_parts):
			series.append(x,bodypart_sets[sorted_parts[x]]/max_sets*10)
		series.append(num_parts,bodypart_sets[sorted_parts[0]]/max_sets*10)
		chart.addSeries(series)
		series.attachAxis(angular_axis)
		series.attachAxis(radial_axis)
		
		max_reps = max(bodypart_reps.values())
		series1 = QLineSeries()
		series1.setName("Reps")
		series1.setPen(QPen(QColor(31,120,180), 2))
		for x in range(0, num_parts):
			series1.append(x,bodypart_reps[sorted_parts[x]]/max_reps*10)
		series1.append(num_parts,bodypart_reps[sorted_parts[0]]/max_reps*10)
		chart.addSeries(series1)
		series1.attachAxis(angular_axis)
		series1.attachAxis(radial_axis)
		
		max_volume = max(bodypart_volume.values())
		series2 = QLineSeries()
		series2.setName("Volume")
		series2.setPen(QPen(QColor(178, 223, 138), 2))
		for x in range(0, num_parts):
			series2.append(x,bodypart_volume[sorted_parts[x]]/max_volume*10)
		series2.append(num_parts,bodypart_volume[sorted_parts[0]]/max_volume*10)
		chart.addSeries(series2)
		series2.attachAxis(angular_axis)
		series2.attachAxis(radial_axis)		




		# new stuff
		bottomseries = QLineSeries()
		bottomseries.append(0,0)
		bottomseries.append(1,0)		
		
		chart.addSeries(bottomseries)
		chart.legend().markers(bottomseries)[0].setVisible(False)
		bottomseries.attachAxis(angular_axis)
		bottomseries.attachAxis(radial_axis)
		
		areaSeries = QAreaSeries(series,bottomseries)
		areaSeries.setPen(QPen(QColor(166,206,227), 2))
		areaSeries.setBrush(QBrush(QColor(166,206,227,50)))
		chart.addSeries(areaSeries)
		chart.legend().markers(areaSeries)[0].setVisible(False)
		
		areaSeries1 = QAreaSeries(series1,bottomseries)
		areaSeries1.setPen(QPen(QColor(31,120,180), 2))
		areaSeries1.setBrush(QBrush(QColor(31,120,180,50)))
		chart.addSeries(areaSeries1)
		chart.legend().markers(areaSeries1)[0].setVisible(False)
		
		areaSeries2 = QAreaSeries(series2,bottomseries)
		areaSeries2.setPen(QPen(QColor(178, 223, 138), 2))
		areaSeries2.setBrush(QBrush(QColor(178, 223, 138,35)))
		chart.addSeries(areaSeries2)
		chart.legend().markers(areaSeries2)[0].setVisible(False)
		#Dunno why this is necessary
		#if max_volume == max(bodypart_volume1.values()): 
		#	areaSeries1.attachAxis(angular_axis)
		#	areaSeries1.attachAxis(radial_axis)
		#else:
		#	areaSeries.attachAxis(angular_axis)
		#	areaSeries.attachAxis(radial_axis)
		
	
	def update_label_positions(self):
		#print(self.width())
		for label in self.labels:
			
		#Labels?
		#text_item = QGraphicsTextItem("some text", parent=chart)
			label[1].setDefaultTextColor(QColor("gray"))
			position_in_chart = self.chart().mapToPosition(label[0], self.reference_series)
			# Rejig the x position
			new_x = position_in_chart.x()
			if(new_x < (self.width()/2)-50-self.chart().legend().boundingRect().width()):
				new_x = new_x-label[1].boundingRect().width()
			elif(new_x < (self.width()/2)+50-self.chart().legend().boundingRect().width()):
				new_x = new_x-label[1].boundingRect().width()/2
			#else:
			#	newlabel[1].setPos(position_in_chart)
				
			# Rejig the y position
			new_y = position_in_chart.y()
			if(new_y < (self.height()/2)-50):
				new_y = new_y-label[1].boundingRect().height()
			elif(new_y < (self.height()/2)+50):
				new_y = new_y-label[1].boundingRect().height()/2
			
			
			label[1].setPos(new_x,new_y)
			
		#print(position_in_chart)


if __name__ == "__main__":
	print("attempting")
	app = QApplication([])
	#chart_view = QChartView(chart)
	chart_view = UTBPlotBodyPartRadar()
	chart_view.draw_months_all(24)
	#chart_view.draw_months_comparision(24, "Volume")
	chart_view.setRenderHint(QPainter.Antialiasing) # for smoother rendering

	print("creating window")

	main_window = QMainWindow()
	main_window.setCentralWidget(chart_view)
	main_window.resize(800,600)
	main_window.show()

	print("executing")



	app.exec()