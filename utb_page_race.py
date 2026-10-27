#!/usr/bin/env python3
"""Under the Bar - Race mode

This file provides the timeline view of workouts with means to compare multiple.

M
"""

import sys
import json
import os
import re
from pathlib import Path
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
	QComboBox,
	QCompleter,
)
from PySide6.QtGui import QPalette, QColor, QPainter
from PySide6 import QtSvgWidgets

import utb_plot_rep_max
import utb_plot_rep_max_year
import utb_plot_cumulative_distance
import utb_plot_cumulative_reps
import utb_plot_pullupchinupyear
import utb_plot_estimated1rm
import utb_plot_thebigthree
import utb_plot_volume_workout
import utb_plot_volume_month
import utb_plot_volume_week
import utb_plot_body_measures
import utb_plot_bodypart_reps
import utb_plot_bodypart_sets
import utb_plot_weightwilks
import utb_plot_workouts
import utb_plot_bodypart_radar
		
class RaceMode(QWidget):

	def __init__(self, color):
		super(RaceMode, self).__init__()
		pagelayout = QVBoxLayout()
		self.setLayout(pagelayout)
		
		self.initialised = False


	def initialise(self):
		
		home_folder = str(Path.home())
		utb_folder = home_folder + "/.underthebar"
		session_data = {}
		if os.path.exists(utb_folder+"/session.json"):	
			with open(utb_folder+"/session.json", 'r') as file:
				session_data = json.load(file)
		else:
			return 403
		user_folder = utb_folder + "/user_" + session_data["user-id"]	
		self.user_folder = utb_folder + "/user_" + session_data["user-id"]	
		account_data = None
		if os.path.exists(user_folder+"/account.json"):	
			with open(user_folder+"/account.json", 'r') as file:
				account_data = json.load(file)
		workoutcount_data = None
		if os.path.exists(user_folder+"/workout_count.json"):	
			with open(user_folder+"/workout_count.json", 'r') as file:
				workoutcount_data = json.load(file)
		
		
		toplayout = QHBoxLayout()
		self.layout().addLayout(toplayout)
		#pagelayout.addStretch()

		
		# Workout 1 selector
		self.workout1Combo = QComboBox()
		self.workout1Combo.setMaxVisibleItems(25)
		self.workout1Combo.setFixedHeight(27)
		self.workout1Combo.setFixedWidth(400)
		self.workout1Combo.addItem("")
		self.workout1Combo.addItem("Load")
		self.workout1Combo.currentIndexChanged.connect(self.selector1Changed)
		###
		self.workout1Combo.setEditable(True)
		self.workout1Combo.setInsertPolicy(QComboBox.NoInsert)
		combo1completer = QCompleter(self.workout1Combo)
		combo1completer.setCompletionMode(QCompleter.PopupCompletion)
		combo1completer.setCaseSensitivity(Qt.CaseInsensitive)
		combo1completer.setFilterMode(Qt.MatchContains)
		combo1completer.setModel(self.workout1Combo.model())
		self.workout1Combo.setCompleter(combo1completer)
		###
		toplayout.addWidget(self.workout1Combo)
		toplayout.addStretch()
		toplayout.addSpacing(100)
		
		# Workout 2 selector
		self.workout2Combo = QComboBox()
		self.workout2Combo.setMaxVisibleItems(25)
		self.workout2Combo.setFixedHeight(27)
		self.workout2Combo.setFixedWidth(400)
		self.workout2Combo.addItem("")
		self.workout2Combo.addItem("Load")
		self.workout2Combo.currentIndexChanged.connect(self.selector2Changed)
		###
		self.workout2Combo.setEditable(True)
		self.workout2Combo.setInsertPolicy(QComboBox.NoInsert)
		combo2completer = QCompleter(self.workout2Combo)
		combo2completer.setCompletionMode(QCompleter.PopupCompletion)
		combo2completer.setCaseSensitivity(Qt.CaseInsensitive)
		combo2completer.setFilterMode(Qt.MatchContains)
		combo2completer.setModel(self.workout2Combo.model())
		self.workout2Combo.setCompleter(combo2completer)
		###
		toplayout.addWidget(self.workout2Combo)
		toplayout.addStretch()
		
		
		self.generateButton  = QPushButton("Generate")
		self.generateButton.setEnabled(False)
		self.generateButton.clicked.connect(self.generate_clicked)
		self.generateButton.setFixedWidth(100)
		toplayout.addWidget(self.generateButton)
		
		script_folder = os.path.split(os.path.abspath(__file__))[0]
		self.script_folder = os.path.split(os.path.abspath(__file__))[0]
		self.svgWidget = QtSvgWidgets.QSvgWidget(script_folder+"/icons/chart-line-solid.svg")
		#self.svgWidget.resize(500,500)
		self.layout().addWidget(self.svgWidget)
		self.currentWidget = self.svgWidget
		
		self.initialised = True
		self.generateButton.setEnabled(True)

	def do_update(self):
		if not self.initialised:
			self.initialise()
			
		# Reload account overview bits
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
		self.workouts_folder = user_folder + "/workouts"
		self.user_folder = user_folder
		
		if os.path.exists(user_folder+"/user_preferences.json"):
			with open(user_folder+"/user_preferences.json", 'r') as file:	
				preference_data = json.load(file)
			self.weight_unit = preference_data["data"]["weight_unit"]
			self.distance_unit = preference_data["data"]["distance_unit"]


		

		
	def graphListRowChanged(self,row):
		print("Defunct graphListRowChanged method")

		
	
	def selector1Changed(self,row):
		#print("optionlist",row)
		if row != -1:
			selectedItemText = self.workout1Combo.itemText(row)
			print(selectedItemText)
			if selectedItemText == "Load":
				self.loadWorkouts()
				self.workout1Combo.showPopup()
	def selector2Changed(self,row):
		#print("optionlist",row)
		if row != -1:
			selectedItemText = self.workout2Combo.itemText(row)
			print(selectedItemText)
			if selectedItemText == "Load":
				self.loadWorkouts()
				self.workout2Combo.showPopup()
			
	def loadWorkouts(self):
		print("Loading workouts", self.workout1Combo.count())
		
		# get dates of relevant workouts
		fileslist = sorted(os.listdir(self.workouts_folder), reverse=True)
		#relevant_workout_dates = []
		#self.relevant_workout_files = {}
		if self.workout1Combo.count() ==2:
			fill_limit = 100
		else:
			fill_limit = len(fileslist)
		
		self.workout_text = {}
		for file in fileslist[:fill_limit]:
			match_workout = re.search('^workout_([A-Za-z0-9_-]+).json\Z',file)
			if match_workout:
				with open(self.workouts_folder+"/"+file, 'r') as loadfile:
					temp_data = json.load(loadfile)
					workout_date = datetime.datetime.fromtimestamp(temp_data["start_time"], datetime.UTC)
					workout_date = workout_date.replace(tzinfo=datetime.timezone.utc).astimezone()
					workout_date_string = workout_date.strftime("%Y-%m-%d")
					#relevant_workout_dates.append(workout_date_string)
					
					#if workout_date_string in self.relevant_workout_files.keys():
					#	self.relevant_workout_files[workout_date_string].append(file)
					#else:
					#	self.relevant_workout_files[workout_date_string] = [file,]
					#print(workout_date.strftime("%Y-%m-%d"))
					
					the_text = workout_date_string + " "  + temp_data["name"]
					self.workout_text[the_text] = file
					
					#if workout_date < new_cal_start_date: #(cal_start_date - datetime.timedelta(weeks=1)):
					#	break
		print(len(self.workout_text.keys()), "workouts loaded")
		
		self.workout1Combo.clear()
		self.workout1Combo.addItems(("","Load"))
		self.workout1Combo.addItems(self.workout_text.keys())
		self.workout2Combo.clear()
		self.workout2Combo.addItems(("","Load"))
		self.workout2Combo.addItems(self.workout_text.keys())
	
	def get_set_text(self, the_set):
		if(the_set["weight_kg"] and the_set["reps"]):
			if self.weight_unit == "kg":
				return str(the_set["reps"])+"x"+str(round(the_set["weight_kg"],2))
			else:
				return str(the_set["reps"])+"x"+str(round(the_set["weight_kg"]*2.20462262,2))
		elif the_set["reps"]:
			return "x" + str(the_set["reps"])
		else:
			return "set"
		
	def generate_clicked(self):
		
		workout1Selected = self.workout1Combo.itemText(self.workout1Combo.currentIndex())
		workout2Selected = self.workout2Combo.itemText(self.workout2Combo.currentIndex())
		print("Generate!", workout1Selected, workout2Selected)
		
		#print(self.workout_text[workout1Selected])
		
		plot1exercises = []
		plot1sets = []
		if workout1Selected != "" and workout1Selected != "Load":
			with open(self.workouts_folder+"/"+self.workout_text[workout1Selected], 'r') as loadfile:
				temp_data = json.load(loadfile)
				
				workout_date = datetime.datetime.fromtimestamp(temp_data["start_time"], datetime.UTC)
				exercise_time = workout_date
				end_time = datetime.datetime.fromtimestamp(temp_data["end_time"], datetime.UTC) - workout_date
				set_time = workout_date
				max_set_time1 = 0
				max_exercise_time1 = 0
				
				starting_rest = 0
				
				for exercise in temp_data["exercises"]:
					planned_rest = exercise["rest_seconds"]
					exercise_rest = 0
					from_start = None
					for set in exercise["sets"]:
						completed_at = datetime.datetime.fromisoformat(set["completed_at"])
						the_delta = completed_at - set_time
						from_start = completed_at - workout_date
						rest_seconds = min(starting_rest, the_delta.total_seconds())
						exercise_rest += rest_seconds
						print("Set", from_start, the_delta, rest_seconds)
						plot1sets.append((self.get_set_text(set), from_start, the_delta, rest_seconds))
						
						starting_rest = planned_rest
						set_time = completed_at
						
						max_set_time1 = max(max_set_time1, the_delta.total_seconds())
					
					exercise_delta = set_time - exercise_time
					print (exercise["title"], from_start, exercise_delta, exercise_rest)
					plot1exercises.append((exercise["title"]+"\n"+str(exercise_delta).split(".")[0].lstrip("0:"), from_start, exercise_delta, exercise_rest))
					exercise_time = set_time
					
					max_exercise_time1 = max(max_exercise_time1, exercise_delta.total_seconds())
		
		plot2exercises = []
		plot2sets = []
		if workout2Selected != "" and workout2Selected != "Load":
			with open(self.workouts_folder+"/"+self.workout_text[workout2Selected], 'r') as loadfile:
				temp_data = json.load(loadfile)
				
				workout_date = datetime.datetime.fromtimestamp(temp_data["start_time"], datetime.UTC)
				exercise_time = workout_date
				end_time = datetime.datetime.fromtimestamp(temp_data["end_time"], datetime.UTC) - workout_date
				set_time = workout_date
				max_set_time2 = 0
				max_exercise_time2 = 0
				
				starting_rest = 0
				
				for exercise in temp_data["exercises"]:
					planned_rest = exercise["rest_seconds"]
					exercise_rest = 0
					from_start = None
					for set in exercise["sets"]:
						completed_at = datetime.datetime.fromisoformat(set["completed_at"])
						the_delta = completed_at - set_time
						from_start = completed_at - workout_date
						rest_seconds = min(starting_rest, the_delta.total_seconds())
						exercise_rest += rest_seconds
						print("Set", from_start, the_delta, rest_seconds)
						plot2sets.append((self.get_set_text(set), from_start, the_delta, rest_seconds))
						
						starting_rest = planned_rest
						set_time = completed_at
						
						max_set_time2 = max(max_set_time2, the_delta.total_seconds())
					
					exercise_delta = set_time - exercise_time
					print (exercise["title"], from_start, exercise_delta, exercise_rest)
					plot2exercises.append((exercise["title"]+"\n"+str(exercise_delta).split(".")[0].lstrip("0:"), from_start, exercise_delta, exercise_rest))
					exercise_time = set_time
					
					max_exercise_time2 = max(max_exercise_time2, exercise_delta.total_seconds())
		
		
		
		# For plotting #1
		if workout1Selected != "" and workout1Selected != "Load":
			plot1times = [datetime.datetime(2000,1,1),]
			plot1values = [0,]
			for the_set in plot1sets:
				plot1times.append(datetime.datetime(2000,1,1)+the_set[1])
				plot1values.append(0)
			plot1times.append(datetime.datetime(2000,1,1)+end_time)
			plot1values.append(0)
		
		# For plotting #2
		if workout2Selected != "" and workout2Selected != "Load":
			plot2times = [datetime.datetime(2000,1,1),]
			plot2values = [0,]
			for the_set in plot1sets:
				plot2times.append(datetime.datetime(2000,1,1)+the_set[1])
				plot2values.append(0)
			plot2times.append(datetime.datetime(2000,1,1)+end_time)
			plot2values.append(0)		
			
		
		plt.style.use('dark_background')

		fig, (ax1, ax2) = plt.subplots(1,2, figsize=(18,9))
		fig, (ax1, ax2) = plt.subplots(1,2,figsize=( self.svgWidget.width()/fig.dpi, self.svgWidget.height()/fig.dpi))

		
		if workout1Selected != "" and workout1Selected != "Load":
			ax1.plot(plot1values, plot1times, "-0", color="white", markerfacecolor="white")
			
			ax1.set_xlim(-150,150)
			#ax.set_ylim(datetime.datetime(2000,1,1), datetime.datetime(2000,1,1)+end_time+end_time)
			
			for the_set in plot1sets:
				ax1.annotate(the_set[0], xy=(0, datetime.datetime(2000,1,1)+the_set[1]), xytext=(the_set[2].total_seconds()/max_set_time1*140, datetime.datetime(2000,1,1)+the_set[1]),
						arrowprops=dict(arrowstyle="-", color="white", linewidth=0.8), va="center", fontsize=6)
						
			for the_ex in plot1exercises:
				#ax.annotate(the_ex[0], xy=(0, datetime.datetime(2000,1,1)+the_ex[1]), xytext=(-50-the_ex[2].total_seconds()/max_exercise_time*100, datetime.datetime(2000,1,1)+the_ex[1]),
				#		arrowprops=dict(arrowstyle="-", color="red", linewidth=0.8), va="center")
				ax1.annotate(the_ex[0], xy=(0, datetime.datetime(2000,1,1)+the_ex[1]), xytext=(-150, datetime.datetime(2000,1,1)+the_ex[1]),
						va="top", ha="left", fontsize=8)		
				ax1.annotate("", xy=(0, datetime.datetime(2000,1,1)+the_ex[1]), xytext=(-150, datetime.datetime(2000,1,1)+the_ex[1]),
						arrowprops=dict(arrowstyle="-", color="white", linewidth=0.8, relpos=(0, 1), zorder=5, shrinkA=0), va="top", ha="left")	
						
			
			ax1.spines[["left"]].set_position(("axes",0.5))
			
			ax1.set_title(workout1Selected, pad=10, loc="left", fontsize=10, fontweight="bold")
			
			ax1.yaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
		else:
			ax1.yaxis.set_visible(False)
		
		if workout2Selected != "" and workout2Selected != "Load":
			ax2.plot(plot2values, plot2times, "-0", color="white", markerfacecolor="white")
			
			ax2.set_xlim(-150,150)
			#ax.set_ylim(datetime.datetime(2000,1,1), datetime.datetime(2000,1,1)+end_time+end_time)
			
			for the_set in plot2sets:
				ax2.annotate(the_set[0], xy=(0, datetime.datetime(2000,1,1)+the_set[1]), xytext=(the_set[2].total_seconds()/max_set_time2*140, datetime.datetime(2000,1,1)+the_set[1]),
						arrowprops=dict(arrowstyle="-", color="white", linewidth=0.8), va="center", fontsize=6)
						
			for the_ex in plot2exercises:
				#ax.annotate(the_ex[0], xy=(0, datetime.datetime(2000,1,1)+the_ex[1]), xytext=(-50-the_ex[2].total_seconds()/max_exercise_time*100, datetime.datetime(2000,1,1)+the_ex[1]),
				#		arrowprops=dict(arrowstyle="-", color="red", linewidth=0.8), va="center")
				ax2.annotate(the_ex[0], xy=(0, datetime.datetime(2000,1,1)+the_ex[1]), xytext=(-150, datetime.datetime(2000,1,1)+the_ex[1]),
						va="top", ha="left", fontsize=8)		
				ax2.annotate("", xy=(0, datetime.datetime(2000,1,1)+the_ex[1]), xytext=(-150, datetime.datetime(2000,1,1)+the_ex[1]),
						arrowprops=dict(arrowstyle="-", color="white", linewidth=0.8, relpos=(0, 1), zorder=5, shrinkA=0), va="top", ha="left")	
						
			
			ax2.spines[["left"]].set_position(("axes",0.5))
			
			ax2.set_title(workout2Selected, pad=10, loc="left", fontsize=10, fontweight="bold")
			
			ax2.yaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
		else:
			ax2.yaxis.set_visible(False)
		
		ax1.spines[["left", "top", "right", "bottom"]].set_visible(False)
		ax2.spines[["left", "top", "right", "bottom"]].set_visible(False)
		ax1.xaxis.set_visible(False)
		ax2.xaxis.set_visible(False)
		ax1.grid(False)		
		ax2.grid(False)
		
		plt.tight_layout()
		fig = plt.gcf()
		
		export_folder = self.user_folder
		fig.savefig(export_folder+'/plot_race.svg', dpi=300)
		
		
		
		self.svgWidget.load(export_folder+'/plot_race.svg')
		return
			


if __name__ == "__main__":
	app = QApplication(sys.argv)
	
	app.setStyle("Fusion")

	# Now use a palette to switch to dark colors:
	palette = QPalette()
	palette.setColor(QPalette.Window, QColor(53, 53, 53))
	palette.setColor(QPalette.WindowText, Qt.white)
	palette.setColor(QPalette.Base, QColor(25, 25, 25))
	palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
	palette.setColor(QPalette.ToolTipBase, Qt.black)
	palette.setColor(QPalette.ToolTipText, Qt.white)
	palette.setColor(QPalette.Text, Qt.white)
	palette.setColor(QPalette.Button, QColor(53, 53, 53))
	palette.setColor(QPalette.ButtonText, Qt.white)
	palette.setColor(QPalette.BrightText, Qt.red)
	palette.setColor(QPalette.Link, QColor(42, 130, 218))
	palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
	palette.setColor(QPalette.HighlightedText, Qt.black)
	app.setPalette(palette)
	
	
	
	window = RaceMode("red")
	window.do_update()
	#window.setFixedSize(800,600)
	window.resize(1200,800)
	window.show()

	app.exec_()
	