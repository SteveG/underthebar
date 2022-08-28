#!/usr/bin/env python3
"""Under the Bar - Analysis

This file provides the analysis page for the application, provides a list of available graphs, a means to generate display.

Methods for generating plots are in separate files, each should contain a generate_options_... method and a generate_plot_... method.

Plots are generated with matplotlib and just stored as a static image. Something dynamic would be better for mouse-over data points
etc but I have not spent much time on looking into that.

There are four areas in this file that need to be edited to add a new plot.
	1. Add to list of plots in initialise(self)
	2. Add plot generation handling to generate_clicked(self)
	3. Generate options plot is selected in graphListRowChanged(self,row) 
	4. Display relevant plot when an option is selected in optionListRowChanged(self,row)
"""

import sys
import json
import os
import re
from pathlib import Path

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QApplication,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
)
from PySide2.QtGui import QPalette, QColor
from PySide2 import QtSvg

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
		
class Analysis(QWidget):

	def __init__(self, color):
		super(Analysis, self).__init__()
		pagelayout = QHBoxLayout()
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
		
		
		sidelayout = QVBoxLayout()
		self.layout().addLayout(sidelayout)
		#pagelayout.addStretch()

		
		self.graphList = QListWidget()
		self.graphList.setFixedWidth(200)
		self.graphList.currentRowChanged.connect(self.graphListRowChanged)
		self.graphList.addItem("Body Measures")
		self.graphList.addItem("Chin-up / Pull-up Year")
		self.graphList.addItem("Cumulative Distance")
		self.graphList.addItem("Cumulative Reps")
		self.graphList.addItem("Estimated One Rep Max")
		self.graphList.addItem("Reps Max Record")
		self.graphList.addItem("Reps Max Record Year")
		self.graphList.addItem("The Big Three")
		self.graphList.addItem("Volume (per Month)")
		self.graphList.addItem("Volume (per Week)")
		self.graphList.addItem("Volume (per Week) Year")
		self.graphList.addItem("Volume (per Workout)")
		self.graphList.addItem("Volume (per Workout) Year")
		self.graphList.setFixedHeight(self.graphList.sizeHintForRow(0) * self.graphList.count() + 2 * self.graphList.frameWidth())
		sidelayout.addWidget(self.graphList)
		
		self.optionList = QListWidget()
		self.optionList.setFixedWidth(200)
		self.optionList.currentRowChanged.connect(self.optionListRowChanged)
		#self.optionList.addItem("Fishing")
		#self.optionList.addItem("Not Fishing")
		sidelayout.addWidget(self.optionList)
		
		self.generateButton  = QPushButton("(re)generate")
		self.generateButton.setEnabled(False)
		self.generateButton.clicked.connect(self.generate_clicked)
		sidelayout.addWidget(self.generateButton)
		
		script_folder = os.path.split(os.path.abspath(__file__))[0]
		self.script_folder = os.path.split(os.path.abspath(__file__))[0]
		self.svgWidget = QtSvg.QSvgWidget(script_folder+"/icons/chart-line-solid.svg")
		#self.svgWidget.resize(500,500)
		self.layout().addWidget(self.svgWidget)
		
		self.initialised = True
		self.graphList.clearSelection()

	def do_update(self):
		if not self.initialised:
			self.initialise()
			
	def generate_clicked(self):
		print("(re)generate!")
		graphSelected = self.graphList.currentItem().text()
		optionSelected = self.optionList.currentItem().text()
		
		if graphSelected == "Reps Max Record":
			utb_plot_rep_max.generate_plot_rep_max(optionSelected, self.svgWidget.width(), self.svgWidget.height())
			filename = "plot_repmax_"+re.sub(r'\W+', '', optionSelected)+'.svg'	
			if os.path.exists(self.user_folder+"/"+filename):	
				self.svgWidget.load(self.user_folder+"/"+filename)
				self.optionList.currentItem().setCheckState(Qt.Checked)
			else:
				self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
		
		elif graphSelected == "Reps Max Record Year":
			utb_plot_rep_max_year.generate_plot_rep_max_year(optionSelected, self.svgWidget.width(), self.svgWidget.height())
			filename = "plot_repmax_year_"+re.sub(r'\W+', '', optionSelected)+'.svg'	
			if os.path.exists(self.user_folder+"/"+filename):	
				self.svgWidget.load(self.user_folder+"/"+filename)
				self.optionList.currentItem().setCheckState(Qt.Checked)
			else:
				self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
		
		elif graphSelected == "The Big Three":
			utb_plot_thebigthree.generate_plot_big3(optionSelected, self.svgWidget.width(), self.svgWidget.height())
			filename = 'plot_big3_alltime.svg'	
			if optionSelected == "All Time - with Brzycki":
				filename = "plot_big3_alltime_brz.svg"
			elif optionSelected == "All Time - with Epley":
				filename = "plot_big3_alltime_ep.svg"	
			if os.path.exists(self.user_folder+"/"+filename):	
				self.svgWidget.load(self.user_folder+"/"+filename)
				self.optionList.currentItem().setCheckState(Qt.Checked)
			else:
				self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
		
		elif graphSelected == "Estimated One Rep Max":
			utb_plot_estimated1rm.generate_plot_est_1rm(optionSelected, self.svgWidget.width(), self.svgWidget.height())
			filename = "plot_est1rm_"+re.sub(r'\W+', '', optionSelected)+'.svg'	
			if os.path.exists(self.user_folder+"/"+filename):	
				self.svgWidget.load(self.user_folder+"/"+filename)
				self.optionList.currentItem().setCheckState(Qt.Checked)
			else:
				self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
		
		elif graphSelected == "Cumulative Distance":
			utb_plot_cumulative_distance.generate_plot_cumulative_distance(optionSelected, self.svgWidget.width(), self.svgWidget.height())
			filename = "plot_cumulativedist_"+re.sub(r'\W+', '', optionSelected)+'.svg'	
			if os.path.exists(self.user_folder+"/"+filename):	
				self.svgWidget.load(self.user_folder+"/"+filename)
				self.optionList.currentItem().setCheckState(Qt.Checked)
			else:
				self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
				
		
		elif graphSelected == "Cumulative Reps":
			utb_plot_cumulative_reps.generate_plot_cumulative_reps(optionSelected, self.svgWidget.width(), self.svgWidget.height())
			filename = "plot_cumulativereps_"+re.sub(r'\W+', '', optionSelected)+'.svg'	
			if os.path.exists(self.user_folder+"/"+filename):	
				self.svgWidget.load(self.user_folder+"/"+filename)
				self.optionList.currentItem().setCheckState(Qt.Checked)
			else:
				self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
				
		elif graphSelected == "Chin-up / Pull-up Year":
			utb_plot_pullupchinupyear.generate_plot_pullupchinupyear(optionSelected, self.svgWidget.width(), self.svgWidget.height())
			filename = "plot_pullupchinupyear_"+optionSelected+'.svg'	
			if os.path.exists(self.user_folder+"/"+filename):	
				self.svgWidget.load(self.user_folder+"/"+filename)
				self.optionList.currentItem().setCheckState(Qt.Checked)
			else:
				self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
		
		elif graphSelected == "Volume (per Workout)":
			utb_plot_volume_workout.generate_plot_volume_workout(optionSelected, self.svgWidget.width(), self.svgWidget.height())
			filename = "plot_volumeworkout_"+re.sub(r'\W+', '', optionSelected)+'.svg'	
			if optionSelected == "--All--":
				filename = "plot_volumeworkout_all.svg"
			if os.path.exists(self.user_folder+"/"+filename):	
				self.svgWidget.load(self.user_folder+"/"+filename)
				self.optionList.currentItem().setCheckState(Qt.Checked)
			else:
				self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
		
		elif graphSelected == "Volume (per Workout) Year":
			utb_plot_volume_workout.generate_plot_volume_workout(optionSelected, self.svgWidget.width(), self.svgWidget.height(), timelimit=True)
			filename = "plot_volumeworkoutyear_"+re.sub(r'\W+', '', optionSelected)+'.svg'	
			if optionSelected == "--All--":
				filename = "plot_volumeworkoutyear_all.svg"
			if os.path.exists(self.user_folder+"/"+filename):	
				self.svgWidget.load(self.user_folder+"/"+filename)
				self.optionList.currentItem().setCheckState(Qt.Checked)
			else:
				self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
		
		elif graphSelected == "Volume (per Week)":
			utb_plot_volume_week.generate_plot_volume_week(optionSelected, self.svgWidget.width(), self.svgWidget.height())
			filename = "plot_volumeweek_"+re.sub(r'\W+', '', optionSelected)+'.svg'	
			if optionSelected == "--All--":
				filename = "plot_volumeweek_all.svg"
			if os.path.exists(self.user_folder+"/"+filename):	
				self.svgWidget.load(self.user_folder+"/"+filename)
				self.optionList.currentItem().setCheckState(Qt.Checked)
			else:
				self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
		
		elif graphSelected == "Volume (per Week) Year":
			utb_plot_volume_week.generate_plot_volume_week(optionSelected, self.svgWidget.width(), self.svgWidget.height(), timelimit=True)
			filename = "plot_volumeweekyear_"+re.sub(r'\W+', '', optionSelected)+'.svg'	
			if optionSelected == "--All--":
				filename = "plot_volumeweekyear_all.svg"
			if os.path.exists(self.user_folder+"/"+filename):	
				self.svgWidget.load(self.user_folder+"/"+filename)
				self.optionList.currentItem().setCheckState(Qt.Checked)
			else:
				self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
		
		elif graphSelected == "Volume (per Month)":
			utb_plot_volume_month.generate_plot_volume_month(optionSelected, self.svgWidget.width(), self.svgWidget.height())
			filename = "plot_volumemonth_"+re.sub(r'\W+', '', optionSelected)+'.svg'	
			if optionSelected == "--All--":
				filename = "plot_volumemonth_all.svg"	
			elif optionSelected == "--All-- (1. Body part)":
				filename = "plot_volumemonth_all_bodypart.svg"
			elif optionSelected == "--All-- (2. Body part prop)":
				filename = "plot_volumemonth_all_bodypartprop.svg"
			if os.path.exists(self.user_folder+"/"+filename):	
				self.svgWidget.load(self.user_folder+"/"+filename)
				self.optionList.currentItem().setCheckState(Qt.Checked)
			else:
				self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
		
		elif graphSelected == "Body Measures":
			utb_plot_body_measures.generate_plot_body_measures(optionSelected, self.svgWidget.width(), self.svgWidget.height())
			filename = "plot_bodymeasures_"+optionSelected+'.svg'	
			if os.path.exists(self.user_folder+"/"+filename):	
				self.svgWidget.load(self.user_folder+"/"+filename)
				self.optionList.currentItem().setCheckState(Qt.Checked)
			else:
				self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
		
		#self.svgWidget.load(self.user_folder+"/plot_repmax_BenchPressDumbbell.svg")
		
	def graphListRowChanged(self,row):
		print(self.graphList.item(row).text(),"graph selected")	
		selected_text = self.graphList.item(row).text()
		
		self.optionList.clear()
		self.optionList.clearSelection()
		self.generateButton.setEnabled(False)
		if selected_text == "Reps Max Record":
			self.options = utb_plot_rep_max.generate_options_rep_max()
			for new_item in sorted(self.options.keys()):
				newOpt = QListWidgetItem(str(new_item))
				newOpt.setFlags(newOpt.flags() | Qt.ItemIsUserCheckable)
				newOpt.setCheckState(Qt.Unchecked)
				if self.options[new_item]:
					newOpt.setCheckState(Qt.Checked)
				self.optionList.addItem(newOpt)
		
		elif selected_text == "Reps Max Record Year":
			self.options = utb_plot_rep_max_year.generate_options_rep_max_year()
			for new_item in sorted(self.options.keys()):
				newOpt = QListWidgetItem(str(new_item))
				newOpt.setFlags(newOpt.flags() | Qt.ItemIsUserCheckable)
				newOpt.setCheckState(Qt.Unchecked)
				if self.options[new_item]:
					newOpt.setCheckState(Qt.Checked)
				self.optionList.addItem(newOpt)
		
		elif selected_text == "The Big Three":
			self.options = utb_plot_thebigthree.generate_options_big3()
			for new_item in sorted(self.options.keys()):
				newOpt = QListWidgetItem(str(new_item))
				newOpt.setFlags(newOpt.flags() | Qt.ItemIsUserCheckable)
				newOpt.setCheckState(Qt.Unchecked)
				if self.options[new_item]:
					newOpt.setCheckState(Qt.Checked)
				self.optionList.addItem(newOpt)
						
		elif selected_text == "Estimated One Rep Max":
			self.options = utb_plot_estimated1rm.generate_options_est_1rm()
			for new_item in sorted(self.options.keys()):
				newOpt = QListWidgetItem(str(new_item))
				newOpt.setFlags(newOpt.flags() | Qt.ItemIsUserCheckable)
				newOpt.setCheckState(Qt.Unchecked)
				if self.options[new_item]:
					newOpt.setCheckState(Qt.Checked)
				self.optionList.addItem(newOpt)
		
		elif selected_text == "Cumulative Distance":
			self.options = utb_plot_cumulative_distance.generate_options_cumulative_distance()
			for new_item in sorted(self.options.keys()):
				newOpt = QListWidgetItem(str(new_item))
				newOpt.setFlags(newOpt.flags() | Qt.ItemIsUserCheckable)
				newOpt.setCheckState(Qt.Unchecked)
				if self.options[new_item]:
					newOpt.setCheckState(Qt.Checked)
				self.optionList.addItem(newOpt)
						
		elif selected_text == "Cumulative Reps":
			self.options = utb_plot_cumulative_reps.generate_options_cumulative_reps()
			for new_item in sorted(self.options.keys()):
				newOpt = QListWidgetItem(str(new_item))
				newOpt.setFlags(newOpt.flags() | Qt.ItemIsUserCheckable)
				newOpt.setCheckState(Qt.Unchecked)
				if self.options[new_item]:
					newOpt.setCheckState(Qt.Checked)
				self.optionList.addItem(newOpt)
				
		elif selected_text == "Chin-up / Pull-up Year":
			self.options = utb_plot_pullupchinupyear.generate_options_pullupchinupyear()
			for new_item in sorted(self.options.keys()):
				newOpt = QListWidgetItem(str(new_item))
				newOpt.setFlags(newOpt.flags() | Qt.ItemIsUserCheckable)
				newOpt.setCheckState(Qt.Unchecked)
				if self.options[new_item]:
					newOpt.setCheckState(Qt.Checked)
				self.optionList.addItem(newOpt)
		
		elif selected_text == "Volume (per Workout)":
			self.options = utb_plot_volume_workout.generate_options_volume_workout()
			for new_item in sorted(self.options.keys()):
				newOpt = QListWidgetItem(str(new_item))
				newOpt.setFlags(newOpt.flags() | Qt.ItemIsUserCheckable)
				newOpt.setCheckState(Qt.Unchecked)
				if self.options[new_item]:
					newOpt.setCheckState(Qt.Checked)
				self.optionList.addItem(newOpt)		
		
		elif selected_text == "Volume (per Workout) Year":
			self.options = utb_plot_volume_workout.generate_options_volume_workout(timelimit=True)
			for new_item in sorted(self.options.keys()):
				newOpt = QListWidgetItem(str(new_item))
				newOpt.setFlags(newOpt.flags() | Qt.ItemIsUserCheckable)
				newOpt.setCheckState(Qt.Unchecked)
				if self.options[new_item]:
					newOpt.setCheckState(Qt.Checked)
				self.optionList.addItem(newOpt)		
			
		elif selected_text == "Volume (per Week)":
			self.options = utb_plot_volume_week.generate_options_volume_week()
			for new_item in sorted(self.options.keys()):
				newOpt = QListWidgetItem(str(new_item))
				newOpt.setFlags(newOpt.flags() | Qt.ItemIsUserCheckable)
				newOpt.setCheckState(Qt.Unchecked)
				if self.options[new_item]:
					newOpt.setCheckState(Qt.Checked)
				self.optionList.addItem(newOpt)		

		elif selected_text == "Volume (per Week) Year":
			self.options = utb_plot_volume_week.generate_options_volume_week(timelimit=True)
			for new_item in sorted(self.options.keys()):
				newOpt = QListWidgetItem(str(new_item))
				newOpt.setFlags(newOpt.flags() | Qt.ItemIsUserCheckable)
				newOpt.setCheckState(Qt.Unchecked)
				if self.options[new_item]:
					newOpt.setCheckState(Qt.Checked)
				self.optionList.addItem(newOpt)	
					
		elif selected_text == "Volume (per Month)":
			self.options = utb_plot_volume_month.generate_options_volume_month()
			for new_item in sorted(self.options.keys()):
				newOpt = QListWidgetItem(str(new_item))
				newOpt.setFlags(newOpt.flags() | Qt.ItemIsUserCheckable)
				newOpt.setCheckState(Qt.Unchecked)
				if self.options[new_item]:
					newOpt.setCheckState(Qt.Checked)
				self.optionList.addItem(newOpt)			
				
		elif selected_text == "Body Measures":
			self.options = utb_plot_body_measures.generate_options_body_measures()
			for new_item in sorted(self.options.keys()):
				newOpt = QListWidgetItem(str(new_item))
				newOpt.setFlags(newOpt.flags() | Qt.ItemIsUserCheckable)
				newOpt.setCheckState(Qt.Unchecked)
				if self.options[new_item]:
					newOpt.setCheckState(Qt.Checked)
				self.optionList.addItem(newOpt)		
		
		self.optionList.clearSelection()
		self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
		
#		home_folder = str(Path.home())
#		utb_folder = home_folder + "/.underthebar"
#		session_data = {}
#		if os.path.exists(utb_folder+"/session.json"):	
#			with open(utb_folder+"/session.json", 'r') as file:
#				session_data = json.load(file)
#		else:
#			return 403
#		user_folder = utb_folder + "/user_" + session_data["user-id"]	
#		
#		self.optionList.clear()
#		
#		if selected_text == "Cumulative Reps":
#			for userfile in sorted(os.listdir(user_folder), reverse=False):
#				#match_user_file = re.search('fito_'+'.*'+'_(....-..-..)_([0-9]+).json',userfile)
#				#if match_user_file:
#				#	raw_fito.append(userfile)
#				self.optionList.addItem(userfile)
#				self.optionList.setCurrentRow(0)
#		elif selected_text == "Reps Max Record":
#			for userfile in sorted(os.listdir(utb_folder), reverse=False):
#				#match_user_file = re.search('fito_'+'.*'+'_(....-..-..)_([0-9]+).json',userfile)
#				#if match_user_file:
#				#	raw_fito.append(userfile)
#				self.optionList.addItem(userfile)
#				self.optionList.setCurrentRow(0)

		
	
	def optionListRowChanged(self,row):
		#print("optionlist",row)
		if row != -1:
			selectedItemText = self.optionList.item(row).text()
			self.generateButton.setEnabled(True)
			if self.graphList.currentItem().text() == "Reps Max Record":
				filename = "plot_repmax_"+re.sub(r'\W+', '', selectedItemText)+'.svg'	
				if os.path.exists(self.user_folder+"/"+filename):	
					self.svgWidget.load(self.user_folder+"/"+filename)
				else:
					self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
			elif self.graphList.currentItem().text() == "Reps Max Record Year":
				filename = "plot_repmax_year_"+re.sub(r'\W+', '', selectedItemText)+'.svg'	
				if os.path.exists(self.user_folder+"/"+filename):	
					self.svgWidget.load(self.user_folder+"/"+filename)
				else:
					self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
			elif self.graphList.currentItem().text() == "The Big Three":
				filename = 'plot_big3_alltime.svg'
				if selectedItemText == "All Time - with Brzycki":
					filename = "plot_big3_alltime_brz.svg"
				elif selectedItemText == "All Time - with Epley":
					filename = "plot_big3_alltime_ep.svg"	
				if os.path.exists(self.user_folder+"/"+filename):	
					self.svgWidget.load(self.user_folder+"/"+filename)
				else:
					self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
			elif self.graphList.currentItem().text() == "Estimated One Rep Max":
				filename = "plot_est1rm_"+re.sub(r'\W+', '', selectedItemText)+'.svg'	
				if os.path.exists(self.user_folder+"/"+filename):	
					self.svgWidget.load(self.user_folder+"/"+filename)
				else:
					self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
			
			elif self.graphList.currentItem().text() == "Cumulative Distance":
				filename = "plot_cumulativedist_"+re.sub(r'\W+', '', selectedItemText)+'.svg'
				if os.path.exists(self.user_folder+"/"+filename):	
					self.svgWidget.load(self.user_folder+"/"+filename)
				else:
					self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
					
			elif self.graphList.currentItem().text() == "Cumulative Reps":
				filename = "plot_cumulativereps_"+re.sub(r'\W+', '', selectedItemText)+'.svg'	
				if os.path.exists(self.user_folder+"/"+filename):	
					self.svgWidget.load(self.user_folder+"/"+filename)
				else:
					self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
					
			elif self.graphList.currentItem().text() == "Chin-up / Pull-up Year":
				filename = "plot_pullupchinupyear_"+re.sub(r'\W+', '', selectedItemText)+'.svg'	
				if os.path.exists(self.user_folder+"/"+filename):	
					self.svgWidget.load(self.user_folder+"/"+filename)
				else:
					self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
					
			
			elif self.graphList.currentItem().text() == "Volume (per Workout)":
				filename = "plot_volumeworkout_"+re.sub(r'\W+', '', selectedItemText)+'.svg'	
				if selectedItemText == "--All--":
					filename = "plot_volumeworkout_all.svg"
				if os.path.exists(self.user_folder+"/"+filename):	
					self.svgWidget.load(self.user_folder+"/"+filename)
				else:
					self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
			
			elif self.graphList.currentItem().text() == "Volume (per Workout) Year":
				filename = "plot_volumeworkoutyear_"+re.sub(r'\W+', '', selectedItemText)+'.svg'	
				if selectedItemText == "--All--":
					filename = "plot_volumeworkoutyear_all.svg"
				if os.path.exists(self.user_folder+"/"+filename):	
					self.svgWidget.load(self.user_folder+"/"+filename)
				else:
					self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
			
			elif self.graphList.currentItem().text() == "Volume (per Week)":
				filename = "plot_volumeweek_"+re.sub(r'\W+', '', selectedItemText)+'.svg'	
				if selectedItemText == "--All--":
					filename = "plot_volumeweek_all.svg"
				if os.path.exists(self.user_folder+"/"+filename):	
					self.svgWidget.load(self.user_folder+"/"+filename)
				else:
					self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")

			elif self.graphList.currentItem().text() == "Volume (per Week) Year":
				filename = "plot_volumeweekyear_"+re.sub(r'\W+', '', selectedItemText)+'.svg'	
				if selectedItemText == "--All--":
					filename = "plot_volumeweekyear_all.svg"
				if os.path.exists(self.user_folder+"/"+filename):	
					self.svgWidget.load(self.user_folder+"/"+filename)
				else:
					self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
					
			elif self.graphList.currentItem().text() == "Volume (per Month)":
				filename = "plot_volumemonth_"+re.sub(r'\W+', '', selectedItemText)+'.svg'	
				if selectedItemText == "--All--":
					filename = "plot_volumemonth_all.svg"
				elif selectedItemText == "--All-- (1. Body part)":
					filename = "plot_volumemonth_all_bodypart.svg"
				elif selectedItemText == "--All-- (2. Body part prop)":
					filename = "plot_volumemonth_all_bodypartprop.svg"
				if os.path.exists(self.user_folder+"/"+filename):	
					self.svgWidget.load(self.user_folder+"/"+filename)
				else:
					self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
			
			elif self.graphList.currentItem().text() == "Body Measures":
				filename = "plot_bodymeasures_"+re.sub(r'\W+', '', selectedItemText)+'.svg'	
				if os.path.exists(self.user_folder+"/"+filename):	
					self.svgWidget.load(self.user_folder+"/"+filename)
				else:
					self.svgWidget.load(self.script_folder+"/icons/chart-line-solid.svg")
					

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
	
	
	

	window = Analysis("red")
	window.do_update()
	#window.setFixedSize(800,600)
	window.resize(1200,800)
	window.show()

	app.exec_()
