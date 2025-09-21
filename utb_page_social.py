#!/usr/bin/env python3
"""Under the Bar - Social Page

This file provides the social page where you can see friends etc.
Copied the profile page to start, so this is a huge mess at the moment. But functions.
"""

import sys
import json
import os
from pathlib import Path
import datetime
import time
import calendar
import re
import xml.etree.ElementTree as ET

from PySide2.QtCore import Qt, QSize, QRect, QItemSelectionModel
from PySide2 import QtSvg
from PySide2.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QLayout,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QWidget,
    QListWidget,
	QListWidgetItem,
    QAbstractItemView,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QToolButton,
	QComboBox,
)
from PySide2.QtGui import QPalette, QColor, QWindow
from PySide2.QtGui import QIcon, QPixmap,QImage, QBrush, QPainter

from PySide2.QtCore import Slot, Signal, QObject, QThreadPool, QRunnable

import hevy_api	
import textwrap
import utb_plot_body_measures
	
		
class Social(QWidget):

	def __init__(self, color):
		super(Social, self).__init__()
		self.script_folder = os.path.split(os.path.abspath(__file__))[0]
		pagelayout = QVBoxLayout()
		self.setLayout(pagelayout)
		#self.setAutoFillBackground(True)
		#palette = self.palette()
		#palette.setColor(QPalette.Window, QColor(color))
		#self.setPalette(palette)
		#self.setMinimumSize(50,50)
		
		
		self.pool = QThreadPool()
		self.initialised = False
	
	def initialise(self):
		#print("Drawing profile page")
		self.deleteItemsOfLayout(self.layout())
		
		home_folder = str(Path.home())
		utb_folder = home_folder + "/.underthebar"
		# workout image stuff, set folder, delete old images
		img_folder = str(Path.home())+ "/.underthebar/temp/"
		if not os.path.exists(img_folder):
			os.makedirs(img_folder)
		for f in os.listdir(img_folder):
			if os.stat(os.path.join(img_folder,f)).st_mtime < time.time() - 14 * 86400:
				os.remove(os.path.join(img_folder,f))
		session_data = {}
		if os.path.exists(utb_folder+"/session.json"):	
			with open(utb_folder+"/session.json", 'r') as file:
				session_data = json.load(file)
		else:
			return 403
		user_folder = utb_folder + "/user_" + session_data["user-id"]	
		workouts_folder = user_folder + "/workouts"	
		self.workouts_folder = user_folder + "/workouts"

		
		
		#pagelayout = QVBoxLayout()
		toplayout = QHBoxLayout()
		self.layout().addLayout(toplayout)
		#self.layout().addStretch()

		toplayout.addStretch()

		# toplayout.addWidget(self.piclabel)
	
		# detailslayout = QVBoxLayout()
		# detailsgrid = QGridLayout()
		# detailsgrid.addWidget(QLabel("<b>User name:</b>"), 0,0)
		# self.usernameLabel = QLabel(account_data["data"]["username"])
		# detailsgrid.addWidget(self.usernameLabel, 0,1)
		# detailsgrid.addWidget(QLabel("<b>Full name:</b>"), 1,0)
		# self.fullnameLabel = QLabel(account_data["data"]["full_name"])
		# detailsgrid.addWidget(self.fullnameLabel, 1,1)
		# detailsgrid.addWidget(QLabel("<b>Description:</b>"), 2,0, Qt.AlignTop)
		# self.detailLabel = QLabel(account_data["data"]["description"])
		# self.detailLabel.setWordWrap(True)
		# self.detailLabel.setFixedWidth(300)
		# detailsgrid.addWidget(self.detailLabel, 2,1)
		# detailsgrid.addWidget(QLabel("<b>Followers:</b>"), 3,0)
		# self.followersLabel = QLabel(str(account_data["data"]["follower_count"]))
		# detailsgrid.addWidget(self.followersLabel, 3,1)
		# detailsgrid.addWidget(QLabel("<b>Following:</b>"), 4,0)
		# self.followingLabel = QLabel(str(account_data["data"]["following_count"]))
		# detailsgrid.addWidget(self.followingLabel, 4,1)
		# detailsgrid.addWidget(QLabel("<b>Workout count:</b>"), 5,0)
		
		# localWorkoutCount = len(os.listdir(self.workouts_folder))
		# self.workoutcountLabel = QLabel()#str(workoutcount_data["data"]["workout_count"]))
		# self.workoutcountLabel.setText("Remote:"+str(workoutcount_data["data"]["workout_count"])+"\tLocal:"+str(localWorkoutCount))
		# detailsgrid.addWidget(self.workoutcountLabel, 5,1)
		
		
		
		# detailslayout.addLayout(detailsgrid)
		# #detailslayout.addStretch()
		# toplayout.addLayout(detailslayout)
		# toplayout.addStretch()
		
		
		
		
		
		# lower layout with feed and stuff
		bottomlayout = QHBoxLayout()
		feedlayout = QVBoxLayout()
		feedbuttonlayout = QHBoxLayout()
		feedbuttonlayout.setSizeConstraint(QLayout.SetMaximumSize)
		
		feedlabel = QtSvg.QSvgWidget(self.script_folder+"/icons/hevy-logo.svg")
		feedlabel.setFixedWidth(80)
		feedlabel.setFixedHeight(19)
		self.reloadbutton = QPushButton()# "Reload feed")
		self.reloadbutton.setIcon(self.loadIcon(self.script_folder+"/icons/arrows-rotate-solid.svg"))
		self.reloadbutton.setFixedWidth(50)
		self.reloadbutton.clicked.connect(self.reload_button)
		
		thetip = """Welcome to the new Social page!

The left column will show mutual friends, i.e. you follow each other!

The next column shows information about changes to your follows
along with non-mutual follows.

The third column shows your squad. Those people who have liked one
of your last 10 workouts, regardless of following state.

Finally, on the right will display a users feed once you select one.

The changes are from when you last reloaded the data using this button"""

		self.reloadbutton.setToolTip(thetip)
		
		# self.feedloadbutton = QPushButton()
		# self.feedloadbutton.setIcon(self.loadIcon(self.script_folder+"/icons/plus-solid.svg"))
		# self.feedloadbutton.setFixedWidth(50)
		# self.feedloadbutton.clicked.connect(self.feed_load_button)
		
		### NEW filter combo box for the calendar
		# self.filterCombo = QComboBox()
		# self.filterCombo.setFixedHeight(27)
		# self.filterCombo.addItem("")
		# self.filterCombo.addItem("Load")
		# self.filterCombo.currentIndexChanged.connect(self.filterChanged)
		###
		feedbuttonlayout.addWidget(feedlabel)
		feedbuttonlayout.addWidget(self.reloadbutton)
		# feedbuttonlayout.addWidget(self.feedloadbutton)
		# feedbuttonlayout.addWidget(self.filterCombo)
		#feedbuttonlayout.addStretch(10)
		feedlayout.addLayout(feedbuttonlayout)
		
		self.friendList = QListWidget()
		self.friendList.setFixedWidth(300)
		#self.friendList.setSelectionMode(QAbstractItemView.NoSelection)
		self.friendList.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
		self.friendList.setAlternatingRowColors(True)
		self.friendList.setFocusPolicy(Qt.NoFocus);
		self.friendList.verticalScrollBar().setSingleStep(15)
		#self.friendList.verticalScrollBar().valueChanged.connect(self.feedScrollChanged) 
		self.friendList.currentRowChanged.connect(self.friendListRowChanged)
		feedlayout.addWidget(self.friendList)
		
		bottomlayout.addLayout(feedlayout)


		self.followList = QListWidget()
		self.followList.setFixedWidth(300)
		#self.followList.setSelectionMode(QAbstractItemView.NoSelection)
		self.followList.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
		self.followList.setAlternatingRowColors(True)
		self.followList.setFocusPolicy(Qt.NoFocus);
		self.followList.verticalScrollBar().setSingleStep(15)
		self.followList.currentRowChanged.connect(self.followListRowChanged)
		bottomlayout.addWidget(self.followList)


		self.squadList = QListWidget()
		self.squadList.setFixedWidth(300)
		#self.squadList.setSelectionMode(QAbstractItemView.NoSelection)
		self.squadList.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
		self.squadList.setAlternatingRowColors(True)
		self.squadList.setFocusPolicy(Qt.NoFocus);
		self.squadList.verticalScrollBar().setSingleStep(15)
		self.squadList.currentRowChanged.connect(self.squadListRowChanged)
		bottomlayout.addWidget(self.squadList)



		
		bottomrightlayout = QVBoxLayout()
		# self.calendarWidget = QTableWidget(8,12)
		# self.calendarWidget.horizontalHeader().hide()
		# self.calendarWidget.horizontalHeader().setMinimumSectionSize(1)
		# #calendarWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents);
		# self.calendarWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);
		# self.calendarWidget.verticalHeader().hide()
		# self.calendarWidget.verticalHeader().setMinimumSectionSize(1)
		# self.calendarWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch);
		# self.calendarWidget.setMaximumHeight(100)
		
		# self.calendarWidget.setSelectionBehavior( QAbstractItemView.SelectItems );
		# self.calendarWidget.setSelectionMode( QAbstractItemView.SingleSelection );
		# self.calendarWidget.itemSelectionChanged.connect(self.calendar_selection)
		# bottomrightlayout.addWidget(self.calendarWidget)
		#bottomrightlayout.addStretch()
		
		bottomcornerlayout = QHBoxLayout()

		self.piclabel = QLabel("image")
		if os.path.exists(user_folder+"/profileimage"):
			pixmap = QPixmap(user_folder+"/profileimage")#.scaled(250,250)
			pixmap = self.makeProfileImage(pixmap)
			self.piclabel.setPixmap(pixmap)
		else:
			script_folder = os.path.split(os.path.abspath(__file__))[0]
			pixmap = QPixmap(script_folder+"/icons/user-solid.svg").scaled(300,300)
			self.piclabel.setPixmap(pixmap)
		self.piclabel.setFixedSize(300,300)

		bottomrightlayout.addWidget(self.piclabel)

		
		bottomcornerlayout.addStretch()

		
		bottomcornerlayout.addStretch()
		self.feedList = QListWidget()
		self.feedList.setFixedWidth(300)
		self.feedList.setSelectionMode(QAbstractItemView.NoSelection)
		self.feedList.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
		self.feedList.setAlternatingRowColors(True)
		self.feedList.setFocusPolicy(Qt.NoFocus);
		self.feedList.verticalScrollBar().setSingleStep(15)
		self.feedList.verticalScrollBar().valueChanged.connect(self.feedScrollChanged)
		bottomcornerlayout.addWidget(self.feedList)
		
		# Change appearance of scroll bars
		#self.ownList.verticalScrollBar().setVisible(False)
		#self.ownList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		#self.measureList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		#self.recordList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		#self.ownList.verticalScrollBar().hide()
		#self.ownList.verticalScrollBar().resize(2, 2)
		
		
		
		#bottomcornerlayout.addStretch()
		
		
		
		
		
		
		
		bottomrightlayout.addLayout(bottomcornerlayout)
		
		
		# populate calendar with dates, starting at day 0 of 52 weeks ago TODO is this too much work for this thread?
		cal_start_date = datetime.datetime.now().astimezone()-datetime.timedelta(weeks=11)
		
#		# get dates of relevant workouts
#		fileslist = sorted(os.listdir(workouts_folder), reverse=True)
		relevant_workout_dates = []
#		self.relevant_workout_files = {}
#		for file in fileslist[:9000]:
#			match_workout = re.search('^workout_([A-Za-z0-9_-]+).json\Z',file)
#			if match_workout:
#				with open(workouts_folder+"/"+file, 'r') as loadfile:
#					temp_data = json.load(loadfile)
#					workout_date = datetime.datetime.utcfromtimestamp(temp_data["start_time"])
#					workout_date = workout_date.replace(tzinfo=datetime.timezone.utc).astimezone()
#					workout_date_string = workout_date.strftime("%Y-%m-%d")
#					relevant_workout_dates.append(workout_date_string)
#					
#					if workout_date_string in self.relevant_workout_files.keys():
#						self.relevant_workout_files[workout_date_string].append(file)
#					else:
#						self.relevant_workout_files[workout_date_string] = [file,]
#					#print(workout_date.strftime("%Y-%m-%d"))
#					
#					if workout_date < (cal_start_date - datetime.timedelta(weeks=1)):
#						break
		
		
		# cal_start_day = cal_start_date.isoweekday()%7
		# cal_start_date = cal_start_date-datetime.timedelta(days=cal_start_day)
		# cal_start_month = cal_start_date.month
		# cal_start_day = cal_start_date.isoweekday()%7
		# week = 0
		# day_count = 0
		# prev_day = 0
		# prev_month = -1
		# week_month_start = 0
		# colour_toggle = True
		
		# self.calendar_link={}
		# for i in range(500):
			# this_date = cal_start_date + datetime.timedelta(days=day_count)
			# this_day = this_date.isoweekday()%7
			# if this_day < prev_day:
				# week +=1
				# if week >=12:
					# break
			# if this_date.month != prev_month:
				# #print("new month",week_month_start,week,this_day)
				# if this_day ==0:
					# if week !=0:
						# self.calendarWidget.setSpan(0, week_month_start, 1, week-week_month_start)
					# #calendarWidget.setItem(0,week_month_start,QTableWidgetItem(calendar.month_name[prev_month]))
					# self.calendarWidget.setItem(0,week,QTableWidgetItem(calendar.month_abbr[this_date.month]))
					# if colour_toggle:
						# self.calendarWidget.item(0,week).setBackground(self.palette().color(QPalette.AlternateBase))
					# else:
						# self.calendarWidget.item(0,week).setBackground(self.palette().color(QPalette.Base))
					# week_month_start = week
				# else:
					# if week != 52:
						# self.calendarWidget.setSpan(0, week_month_start, 1, week-week_month_start+1)
						# #calendarWidget.setItem(0,week_month_start,QTableWidgetItem(calendar.month_name[prev_month]))
						# self.calendarWidget.setItem(0,week+1,QTableWidgetItem(calendar.month_abbr[this_date.month]))
						# #if self.calendarWidget.item(0, week+1) != None:
						# if colour_toggle:
							# self.calendarWidget.item(0,week+1).setBackground(self.palette().color(QPalette.AlternateBase))
						# else:
							# self.calendarWidget.item(0,week+1).setBackground(self.palette().color(QPalette.Base))
						# week_month_start = week+1
				
				# colour_toggle = not colour_toggle
				# prev_month = this_date.month
			# prev_day = this_day
			# #self.calendarWidget.setItem(this_day+1,week,QTableWidgetItem(str(this_date.day)))
			# self.calendarWidget.setItem(this_day+1,week,QTableWidgetItem())
			# if self.calendarWidget.item(this_day+1,week) == None:
				# break
			# if this_date.strftime("%Y-%m-%d") in relevant_workout_dates:
# #				self.calendarWidget.item(this_day+1,week).setBackground(self.palette().color(QPalette.ToolTipBase))
# #				self.calendar_link[(this_day+1,week)]=this_date.strftime("%Y-%m-%d")
# #				if this_date.strftime("%Y-%m-%d") == relevant_workout_dates[0]:
# #					self.calendarWidget.setCurrentCell(this_day+1,week,QItemSelectionModel.ClearAndSelect)
# #					#print("date of last workout",this_date.strftime("%Y-%m-%d"))
				# pass
			# elif colour_toggle:
				# self.calendarWidget.item(this_day+1,week).setBackground(self.palette().color(QPalette.Base))
			# else:
				# self.calendarWidget.item(this_day+1,week).setBackground(self.palette().color(QPalette.AlternateBase))
			# day_count += 1
		# self.calendarWidget.setSpan(0, week_month_start, 1, 12-week_month_start)
		
		
		bottomlayout.addLayout(bottomrightlayout)
		#bottomlayout.addStretch()
		
		self.layout().addLayout(bottomlayout)
		
		self.feed_last_index = 0
		
		self.initialised = True
		self.do_update()

	def do_update(self):
		print("updating")
		if not self.initialised:
			self.initialise()
		else:
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
			
			# Unit preferences
			if os.path.exists(user_folder+"/user_preferences.json"):
				with open(user_folder+"/user_preferences.json", 'r') as file:	
					preference_data = json.load(file)
				self.weight_unit = preference_data["data"]["weight_unit"]
				self.distance_unit = preference_data["data"]["distance_unit"]
				self.body_measurement_unit = preference_data["data"]["body_measurement_unit"]
			else:
				self.weight_unit = "kg"
			
			# Get Following Data
			following_data = {}
			if os.path.exists(user_folder+"/following.json"):	
				with open(user_folder+"/following.json", 'r') as file:
					following_data = json.load(file)
			# Get Follower Data
			follower_data = {}
			if os.path.exists(user_folder+"/follower.json"):	
				with open(user_folder+"/follower.json", 'r') as file:
					follower_data = json.load(file)
			# Build Mutual Friend List
			mutual_friends = []
			following_only = []
			follower_only = []
			for user in following_data["data"]:
				if user in follower_data["data"]:
					mutual_friends.append(user)
				else:
					following_only.append(user)
			for user in follower_data["data"]:
				if user not in mutual_friends:
					follower_only.append(user)
			print(len(mutual_friends),"mutual friends,",len(following_only),"you follow, and",len(follower_only),"follow you.")
			
			# Suggested Users
			suggested_data = {}
			if os.path.exists(user_folder+"/suggested_users.json"):	
				with open(user_folder+"/suggested_users.json", 'r') as file:
					suggested_data = json.load(file)
			suggested = []
			for user in suggested_data["data"]:
				suggested.append(user["username"])
			suggested = sorted(suggested)
			
			
			# Clear the lists
			self.friendList.clear()
			self.followList.clear()
			self.squadList.clear()
			
			# Populate the interface lists
			label = QListWidgetItem("------Mutual Friends------")
			label.setTextAlignment(Qt.AlignCenter)
			self.friendList.addItem(label)
			self.friendList.addItems(mutual_friends)
				
			# Populate the follows list (recent changes, and non-mutual)
			# Changes first
			label = QListWidgetItem("------Suggested Users------")
			label.setTextAlignment(Qt.AlignCenter)
			self.followList.addItem(label)
			self.followList.addItems(suggested)
			label = QListWidgetItem("------Newly Following------")
			label.setTextAlignment(Qt.AlignCenter)
			self.followList.addItem(label)
			self.followList.addItems(following_data["added"])
			label = QListWidgetItem("------Stopped Following------")
			label.setTextAlignment(Qt.AlignCenter)
			self.followList.addItem(label)
			self.followList.addItems(following_data["removed"])
			label = QListWidgetItem("------New Follower------")
			label.setTextAlignment(Qt.AlignCenter)
			self.followList.addItem(label)
			self.followList.addItems(follower_data["added"])
			label = QListWidgetItem("------Lost Follower------")
			label.setTextAlignment(Qt.AlignCenter)
			self.followList.addItem(label)
			self.followList.addItems(follower_data["removed"])
			# Then the non mutual lists
			label = QListWidgetItem("------You Follow------")
			label.setTextAlignment(Qt.AlignCenter)
			self.followList.addItem(label)
			self.followList.addItems(following_only)
			label = QListWidgetItem("------Follow You------")
			label.setTextAlignment(Qt.AlignCenter)
			self.followList.addItem(label)
			self.followList.addItems(follower_only)
			
			
			# Do the Squad List
			squad_data = {}
			if os.path.exists(user_folder+"/squad.json"):	
				with open(user_folder+"/squad.json", 'r') as file:
					squad_data = json.load(file)
			# Changes First
			label = QListWidgetItem("------New Member------")
			label.setTextAlignment(Qt.AlignCenter)
			self.squadList.addItem(label)
			#self.squadList.addItems(sorted(squad_data["added"]))
			new_squad = []
			for user in sorted(squad_data["added"]):
				if squad_data["following_data"][user] == "not-following":
					#new_squad.append(str(squad_data["data"][user]*10)+"% "+user + " (not following)")
					new_squad.append(user + " (not following)")
				else:
					#new_squad.append(str(squad_data["data"][user]*10)+"% "+user)
					new_squad.append(user)
			self.squadList.addItems(new_squad)
			label = QListWidgetItem("------Lost Member------")
			label.setTextAlignment(Qt.AlignCenter)
			self.squadList.addItem(label)
			self.squadList.addItems(sorted(squad_data["removed"]))
			label = QListWidgetItem("------Your Squad------")
			label.setTextAlignment(Qt.AlignCenter)
			self.squadList.addItem(label)
			squad_list = []
			last_score = None
			for user in squad_data["data"].keys():
				score = squad_data["data"][user]*10
				if score != last_score:
					label = QListWidgetItem("------"+str(score)+"%------")
					label.setTextAlignment(Qt.AlignCenter)
					self.squadList.addItem(label)
					last_score = score
				if squad_data["following_data"][user] == "not-following":
					#squad_list.append(user + " (not following)")
					self.squadList.addItem(user + " (not following)")
				else:
					#squad_list.append(user)
					self.squadList.addItem(user)
			#self.squadList.addItems(squad_list)
			
			
			self.feedloading = False
			return
			
			# account_data = None
			# if os.path.exists(user_folder+"/account.json"):	
				# with open(user_folder+"/account.json", 'r') as file:
					# account_data = json.load(file)
					# if "full_name" not in account_data["data"]:
						# account_data["data"]["full_name"] = ""
					# if "description" not in account_data["data"]:
						# account_data["data"]["description"] = ""
				# self.usernameLabel.setText(account_data["data"]["username"])
				# self.fullnameLabel.setText(account_data["data"]["full_name"])
				# self.detailLabel.setText(account_data["data"]["description"])
				# self.followersLabel.setText(str(account_data["data"]["follower_count"]))
				# self.followingLabel.setText(str(account_data["data"]["following_count"]))
			# else:
				# self.usernameLabel.setText("Download account data")
			# workoutcount_data = None
			# if os.path.exists(user_folder+"/workout_count.json"):	
				# with open(user_folder+"/workout_count.json", 'r') as file:
					# workoutcount_data = json.load(file)
				# localWorkoutCount = len(os.listdir(self.workouts_folder))
				# self.workoutcountLabel.setText("Remote:"+str(workoutcount_data["data"]["workout_count"])+"\tLocal:"+str(localWorkoutCount))
			# else:
				# self.workoutcountLabel.setText("Download workout count")
			# here we are going to get the preferred units of the user

			#self.workoutcountLabel.setText(str(workoutcount_data["data"]["workout_count"]))
			
			
			
			
			
			
			
			try:
				selected_index = self.calendarWidget.selectedIndexes()[0]
				self.calendarWidget.blockSignals(True)
			except:
				selected_index = None
			self.calendarWidget.clear()
			self.calendarWidget.clearSpans()
			#self.calendarWidget.setCurrentCell(selected_index.row(), selected_index.column(),QItemSelectionModel.ClearAndSelect)
			#pass
			# Reload calendar bit
			
			
			
			# populate calendar with dates, starting at day 0 of 52 weeks ago TODO is this too much work for this thread?
			cal_start_date = datetime.datetime.now().astimezone()-datetime.timedelta(weeks=11)
			#print("starting date",cal_start_date)
			new_cal_start_date = cal_start_date.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
			#print("new starting_date", new_cal_start_date)
			
			# get dates of relevant workouts
			fileslist = sorted(os.listdir(workouts_folder), reverse=True)
			relevant_workout_dates = []
			self.relevant_workout_files = {}
			for file in fileslist[:9000]:
				match_workout = re.search('^workout_([A-Za-z0-9_-]+).json\Z',file)
				if match_workout:
					with open(workouts_folder+"/"+file, 'r') as loadfile:
						temp_data = json.load(loadfile)
						workout_date = datetime.datetime.utcfromtimestamp(temp_data["start_time"])
						workout_date = workout_date.replace(tzinfo=datetime.timezone.utc).astimezone()
						workout_date_string = workout_date.strftime("%Y-%m-%d")
						relevant_workout_dates.append(workout_date_string)
						
						if workout_date_string in self.relevant_workout_files.keys():
							self.relevant_workout_files[workout_date_string].append(file)
						else:
							self.relevant_workout_files[workout_date_string] = [file,]
						#print(workout_date.strftime("%Y-%m-%d"))
						
						if workout_date < new_cal_start_date: #(cal_start_date - datetime.timedelta(weeks=1)):
							break
			
			
			cal_start_day = cal_start_date.isoweekday()%7
			cal_start_date = cal_start_date-datetime.timedelta(days=cal_start_day)
			cal_start_month = cal_start_date.month
			cal_start_day = cal_start_date.isoweekday()%7
			week = 0
			day_count = 0
			prev_day = 0
			prev_month = -1
			week_month_start = 0
			colour_toggle = True
			
			self.calendar_link={}
			for i in range(380):
				this_date = cal_start_date + datetime.timedelta(days=day_count)
				this_day = this_date.isoweekday()%7
				if this_day < prev_day:
					week +=1
					if week >=12:
						break
				if this_date.month != prev_month:
					#print("new month",week_month_start,week,this_day)
					if this_day ==0:
						if week !=0:
							self.calendarWidget.setSpan(0, week_month_start, 1, week-week_month_start)
						#calendarWidget.setItem(0,week_month_start,QTableWidgetItem(calendar.month_name[prev_month]))
						self.calendarWidget.setItem(0,week,QTableWidgetItem(calendar.month_abbr[this_date.month]))
						self.calendar_link[(0,week)]=this_date.strftime("%Y-%m")
						if colour_toggle:
							self.calendarWidget.item(0,week).setBackground(self.palette().color(QPalette.AlternateBase))
						else:
							self.calendarWidget.item(0,week).setBackground(self.palette().color(QPalette.Base))
						week_month_start = week
					else:
						if week != 52:
							self.calendarWidget.setSpan(0, week_month_start, 1, week-week_month_start+1)
							#calendarWidget.setItem(0,week_month_start,QTableWidgetItem(calendar.month_name[prev_month]))
							self.calendarWidget.setItem(0,week+1,QTableWidgetItem(calendar.month_abbr[this_date.month]))
							self.calendar_link[(0,week+1)]=this_date.strftime("%Y-%m")
							if colour_toggle:
								self.calendarWidget.item(0,week+1).setBackground(self.palette().color(QPalette.AlternateBase))
							else:
								self.calendarWidget.item(0,week+1).setBackground(self.palette().color(QPalette.Base))
							week_month_start = week+1
					
					colour_toggle = not colour_toggle
					prev_month = this_date.month
				prev_day = this_day
				#calendarWidget.setItem(this_day+1,week,QTableWidgetItem(str(this_date.day)))
				self.calendarWidget.setItem(this_day+1,week,QTableWidgetItem())
				if self.calendarWidget.item(this_day+1,week) == None:
					break
				if this_date.strftime("%Y-%m-%d") in relevant_workout_dates:
					self.calendarWidget.item(this_day+1,week).setBackground(self.palette().color(QPalette.ToolTipBase))
					self.calendar_link[(this_day+1,week)]=this_date.strftime("%Y-%m-%d")
					
					### NEW check if a filtered item???, if its highlight it
					if self.filterCombo.currentIndex() != 0:
						#print("NEED TO APPLY FILTER", self.filterCombo.currentText())
						for file in self.relevant_workout_files[this_date.strftime("%Y-%m-%d")]:
							#print(file)
							with open(self.workouts_folder+"/"+file, 'r') as loadfile:
								temp_data = json.load(loadfile)
								if self.has_filtereditem(temp_data, self.filterCombo.currentText()):
									self.calendarWidget.item(this_day+1,week).setBackground(QColor("midnightblue").darker(200))
								
								#fancystring += self.get_fancy_text(temp_data)
								# body picture
								#body_things = self.get_bodyparts(temp_data)
								#bodypart_list = bodypart_list + body_things[0]
								#other_bodypart_list = other_bodypart_list + body_things[1]
					###
					
					if this_date.strftime("%Y-%m-%d") == relevant_workout_dates[0]:
						self.calendarWidget.setCurrentCell(this_day+1,week,QItemSelectionModel.ClearAndSelect)
						#print("date of last workout",this_date.strftime("%Y-%m-%d"))
				elif colour_toggle:
					self.calendarWidget.item(this_day+1,week).setBackground(self.palette().color(QPalette.Base))
				else:
					self.calendarWidget.item(this_day+1,week).setBackground(self.palette().color(QPalette.AlternateBase))
				day_count += 1
			self.calendarWidget.setSpan(0, week_month_start, 1, 12-week_month_start)	
			
			
			self.calendarWidget.blockSignals(False)
			if selected_index != None:
				self.calendarWidget.setCurrentCell(selected_index.row(), selected_index.column(),QItemSelectionModel.ClearAndSelect)
			
			
			
			# Body measurements
			self.measureList.clear()
			
			try:
				utb_plot_body_measures.generate_bodyweight_small()
		
				bodypicitem = QListWidgetItem()
				bodypic = QtSvg.QSvgWidget(user_folder+"/plot_bodyweight_small.svg")
				bodypic.setToolTip("Body weight\n20 most recent")
				#bodypic.load(svgbecomes)
				bodypic.setFixedWidth(300)
				bodypic.setFixedHeight(200)
				bodypicitem.setSizeHint(QSize(200,200))
				self.measureList.addItem(bodypicitem)
				self.measureList.setItemWidget(bodypicitem,bodypic)
			except:
			    print("error loading bodyweight graph")
			
			# Body measurements
			
			if os.path.exists(user_folder+"/body_measurements.json"):	
				with open(user_folder+"/body_measurements.json", 'r') as file:
					
					measure_data = json.load(file)["data"]
					measure_data.reverse()
					measure_string = "Body Measurements\n"
					
					for measure_set in measure_data:
						measure_string += "\n"
						measure_string += "    " + str("Date").replace("_"," ").title() +": "+ str(measure_set["date"]) + "\n        "
						the_keys = list(measure_set.keys())
						
						for measurekey in the_keys:
							if measure_set[measurekey] != None:
								if measurekey == "weight_kg" and self.weight_unit=="lbs":
									lb = round(measure_set[measurekey]*2.20462262,2)
									if lb.is_integer():
										lb = int(lb)
									measure_string += "    " + "Weight Lb" +": "+ str(lb) + "\n        "
								elif measurekey in ("user_id","id","date","created_at"):
									None
								else:
									measure_string += "    " + measurekey.replace("_"," ").title() +": "+ str(measure_set[measurekey]) + "\n        "
					self.measureList.addItem(measure_string)
						#id_records[record["exercise_template_id"]] = [record["type"],record["record"]]
			else:
				self.measureList.addItem("\nDownload body measurements. \nBottom left gear icon.")
			
			# populate PR list
			self.recordList.clear()
			if os.path.exists(user_folder+"/set_personal_records.json"):	
			
				# get recent exercises
				fileslist = sorted(os.listdir(workouts_folder), reverse=True)
				self.workoutList_files = []
				self.exercises = {}
				self.exercisesHevyID = {}
				counter = 0
				for file in fileslist[:70]:
					#if len(self.exercises) >7:
					#	break
					match_workout = re.search('^workout_([A-Za-z0-9_-]+).json\Z',file)
					if match_workout:
						with open(workouts_folder+"/"+file, 'r') as file:
							temp_data = json.load(file)
							workout_date = datetime.datetime.utcfromtimestamp(temp_data["start_time"])
							workout_date = workout_date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
							if counter < 20:
								temp_index = temp_data["index"]
								#self.recordList.addItem(temp_data["name"]+"-"+workout_date.strftime("%a %b %-d, %Y, %-I%P"))
								
								self.workoutList_files.append(file)
							
							for exercise in temp_data["exercises"]:
								exercise_title = exercise["title"]
								if exercise_title == "Standing Calf Raise":
									print(workout_date)
								if exercise_title not in self.exercises.keys():
									self.exercises[exercise_title] = workout_date.strftime("%a %b %#d, ") + str(len(exercise["sets"])) + " sets"
								
								if exercise_title not in self.exercisesHevyID.keys():
									self.exercisesHevyID[exercise_title] = exercise["exercise_template_id"]

					counter += 1
				
				
				
				# PRs from hevy
				id_records = {}
				with open(user_folder+"/set_personal_records.json", 'r') as file:
					records_data = json.load(file)["data"]
					for record in records_data:
						#id_records[record["exercise_template_id"]] = [record["type"],record["record"]]
						old_value = id_records.get(record["exercise_template_id"],[])
						old_value.append([record["type"],record["record"]])
						id_records[record["exercise_template_id"]] = old_value
				
				self.recordList.addItem("\nPersonal Records")						
				for exercise_title in sorted(self.exercises.keys()):
					hevy_id = self.exercisesHevyID[exercise_title]
					if hevy_id not in id_records.keys():
						print(exercise_title)
						fancy_string = "\n    "+exercise_title
						fancy_string += "\n        Missing from hevy data"
						self.recordList.addItem(fancy_string)
						continue
					
					fancy_string = "\n    "+exercise_title
					for record_set in id_records[hevy_id]:
						record_type = record_set[0]
						record_value = record_set[1]
					
						
						if "weight" in record_type and self.weight_unit == "lbs":
							lb = round(record_value*2.20462262,2)
							if lb.is_integer():
								lb = int(lb)
							record_value = lb
							#fancy_string += "\n        " + "Best Weight"+": "+str(lb)
						#else:
						fancy_string += "\n        " + record_type.replace("_"," ").title()+": "+str(record_value)
					#fancy_string += "\n    Last workout: "+ self.exercises[exercise_title]
					#fancy_string += "\n    Record type: "+ record_type
					#fancy_string += "\n    Record value: "+ str(record_value)
					self.recordList.addItem(fancy_string)
			else:
				self.recordList.addItem("\nDownload personal records, \nBottom left gear icon.")
		
			#update user profile image		
			if os.path.exists(user_folder+"/profileimage"):
				pixmap = QPixmap(user_folder+"/profileimage")#.scaled(250,250)
				pixmap = self.makeProfileImage(pixmap)
				self.piclabel.setPixmap(pixmap)
			else:
				script_folder = os.path.split(os.path.abspath(__file__))[0]
				pixmap = QPixmap(script_folder+"/icons/user-solid.svg").scaled(250,250)
				self.piclabel.setPixmap(pixmap)
			
	
	def deleteItemsOfLayout(self, layout):
		if layout is not None:
			while layout.count():
				item = layout.takeAt(0)
				widget = item.widget()
				if widget is not None:
					widget.setParent(None)
				else:
					self.deleteItemsOfLayout(item.layout())

	def filterChanged(self, index):
		print("filter changed", index)
		
		if index ==0:
			print("nothing selected in filter")
			self.do_update()
		elif index ==1 and self.filterCombo.currentText()=="Load":
			print("do the load...")
			
			bodyparts = []
			exercises = []
			
			for the_date in self.relevant_workout_files.keys():
				for file in self.relevant_workout_files[the_date]:
					with open(self.workouts_folder+"/"+file, 'r') as loadfile:
						temp_data = json.load(loadfile)
						temp_exercises, temp_bp = self.get_exercisesandbodyparts(temp_data)
						
						for exercise in temp_exercises:
							if exercise not in exercises:
								exercises.append(exercise)
						for bodypart in temp_bp:
							if bodypart not in bodyparts:
								bodyparts.append(bodypart)
			
			self.filterCombo.addItems(sorted(bodyparts))
			self.filterCombo.insertSeparator(self.filterCombo.count())
			self.filterCombo.addItems(sorted(exercises))
			
			self.filterCombo.blockSignals(True)
			self.filterCombo.setCurrentIndex(0)
			self.filterCombo.removeItem(1)
			self.filterCombo.showPopup()
			self.filterCombo.blockSignals(False)
			
		else:
			print("selected filter item", self.filterCombo.currentText())
			filterText = self.filterCombo.currentText()
			self.do_update()
	
			
	def friendListRowChanged(self, row):
		if not self.friendList.item(row):
			return
		print("friendListRowChanged", row, self.friendList.item(row).text())
		self.followList.clearSelection()
		self.squadList.clearSelection()
		self.current_user = str(self.friendList.item(row).text())
		self.feed_reload_button()
		
	def followListRowChanged(self, row):
		if not  self.followList.item(row):
			return
		print("followListRowChanged", row, self.followList.item(row).text())
		self.friendList.clearSelection()
		self.squadList.clearSelection()
		the_text = str(self.followList.item(row).text())
		if the_text.startswith("------"):
			return
		else:
			self.current_user = the_text
			self.feed_reload_button()
	
	def squadListRowChanged(self, row):
		if not self.squadList.item(row):
			return
		print("squadListRowChanged", row, self.squadList.item(row).text())
		self.followList.clearSelection()
		self.friendList.clearSelection()
		the_text = str(self.squadList.item(row).text())
		print(the_text,the_text.startswith("------"),the_text.endswith(" (not following)"))
		if the_text.startswith("------"):
			return
		elif the_text.endswith(" (not following)"):
			self.current_user = the_text[:-16]
			self.feed_reload_button()
		else:
			self.current_user = the_text
			self.feed_reload_button()
	
	def calendar_selection(self):
		the_item = self.calendarWidget.selectedItems()[0]
		selected_index = self.calendarWidget.selectedIndexes()[0]
		selected_cell = (selected_index.row(), selected_index.column())
		if selected_cell not in self.calendar_link.keys():
			return
			
		the_date = self.calendar_link[selected_cell]
		print("Selection changed",the_date)
		
		if selected_cell[0] == 0: # month selected
			print("Month view!")
			
			workout_count = 0
			exercises = {}
			bodypart_list = []
			other_bodypart_list = []
			
			for key in self.relevant_workout_files.keys():
				if key.startswith(the_date):
					
					#print(key)
					#the_file = str(self.relevant_workout_files[key])
					for file in self.relevant_workout_files[key]:
						workout_count +=1
						with open(self.workouts_folder+"/"+file, 'r') as loadfile:
							temp_data = json.load(loadfile)
							# body picture
							body_things = self.get_bodyparts(temp_data)
							bodypart_list = bodypart_list + body_things[0]
							other_bodypart_list = other_bodypart_list + body_things[1]
					        # basic data
							basics = self.get_basic_workout_stats(temp_data)
							for exercise in basics.keys():
								if exercise not in exercises.keys():
									exercises[exercise] = basics[exercise]
								else:
									exercises[exercise] += basics[exercise]
			like_count = exercises["like_count"]
			del exercises["like_count"]
			comment_count = exercises["comment_count"]
			del exercises["comment_count"]
			sorted_exercises = dict(sorted(exercises.items(), key=lambda item: item[1], reverse=True))
			
			fancystring = "Month Summary: "+ the_date
			fancystring += "\n\n    Workouts completed: " + str(workout_count)
			fancystring += "\n\n    Exercises: \n"
			for s_ex in sorted_exercises.keys():
				fancystring += "\n        "+s_ex+": "+str(sorted_exercises[s_ex]) + " sets"
			fancystring += "\n\n    Social: " + str(like_count) + " prop(s), " + str(comment_count) + " comment(s)"
			self.ownList.clear()
			
			#body picture stuff
			tree = ET.parse(self.script_folder+"/icons/fullbody.svg")
			root = tree.getroot()
			
			for child in root:
				if child.attrib["id"] in other_bodypart_list:#["chest"]:
					for sub_child in child:
						sub_child.attrib["fill"] = "midnightblue"
				if child.attrib["id"] in bodypart_list:#["chest"]:
					for sub_child in child:
						sub_child.attrib["fill"] = "#2A82DA"
			svgbecomes = ET.tostring(root)
			
			bodypicitem = QListWidgetItem()
			bodypic = QtSvg.QSvgWidget()
			bodypic.setToolTip("Light - Targeted Muscle\nDark - Secondary Muscle\nBlack - No Activity")
			bodypic.load(svgbecomes)
			bodypic.setFixedWidth(300)
			bodypic.setFixedHeight(200)
			bodypicitem.setSizeHint(QSize(200,200))
			self.ownList.addItem(bodypicitem)
			self.ownList.setItemWidget(bodypicitem,bodypic)
			
			self.ownList.addItem(fancystring)
			
		else: # single day selected
		
			fancystring = ""
			bodypart_list = []
			other_bodypart_list = []
			
			for file in self.relevant_workout_files[the_date]:
				with open(self.workouts_folder+"/"+file, 'r') as loadfile:
					temp_data = json.load(loadfile)
					fancystring += self.get_fancy_text(temp_data)
					# body picture
					body_things = self.get_bodyparts(temp_data)
					bodypart_list = bodypart_list + body_things[0]
					other_bodypart_list = other_bodypart_list + body_things[1]
					#print("\n\n"+fancystring)
			self.ownList.clear()
			#self.ownList.addItem("body here")
			
			
			#print(bodypart_list,other_bodypart_list)
			
			
			tree = ET.parse(self.script_folder+"/icons/fullbody.svg")
			root = tree.getroot()
			
			for child in root:
				if child.attrib["id"] in other_bodypart_list:#["chest"]:
					for sub_child in child:
						sub_child.attrib["fill"] = "midnightblue"
				if child.attrib["id"] in bodypart_list:#["chest"]:
					for sub_child in child:
						sub_child.attrib["fill"] = "#2A82DA"
			svgbecomes = ET.tostring(root)
			
			bodypicitem = QListWidgetItem()
			bodypic = QtSvg.QSvgWidget()
			bodypic.setToolTip("Light - Targeted Muscle\nDark - Secondary Muscle\nBlack - No Activity")
			bodypic.load(svgbecomes)
			bodypic.setFixedWidth(300)
			bodypic.setFixedHeight(200)
			bodypicitem.setSizeHint(QSize(200,200))
			self.ownList.addItem(bodypicitem)
			self.ownList.setItemWidget(bodypicitem,bodypic)
			
			
			self.ownList.addItem(fancystring)
					
	
	def get_basic_workout_stats(self, workoutjson):
		workout = workoutjson
		exercises = {}
		for exercise in workout["exercises"]:
			if exercise["title"] not in exercises.keys():
				exercises[exercise["title"]] = len(exercise["sets"])
			else:
				exercises[exercise["title"]] += len(exercise["sets"])
		exercises["like_count"] = workout["like_count"]
		exercises["comment_count"] = workout["comment_count"]
		return exercises
	
	# this is used when clicking on the calendar widget, text is shown for that workout day
	def get_fancy_text(self, workoutjson):
		workout = workoutjson
		#fancystring = "\n"+workout["username"] + " - " + workout["name"]
		fancystring = workout["name"]
		workout_date = datetime.datetime.utcfromtimestamp(workout["start_time"])
		workout_date = workout_date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
		
		import platform
		if platform.system() == "Linux":
			fancystring += "\n" + workout_date.strftime("%a %b %-d, %Y, %-I%P, ") + str(len(workout["exercises"])) + " exercises"
		else:
			fancystring += "\n" + workout_date.strftime("%a %b %#d, %Y, %I%p, ") + str(len(workout["exercises"])) + " exercises"
		
		if workout["description"] != "":
			stringlist = textwrap.wrap(workout["description"], width=50,initial_indent="     " ,subsequent_indent="     ")
			fancystring += "\n"
			for substring in stringlist:
				fancystring += "\n"+substring
		
		the_superset_id = None
		ss_string = " "
		for exercise in workout["exercises"]:
			if exercise["superset_id"] != None:
				ss_string = "|"
				if exercise["superset_id"] != the_superset_id:
					the_superset_id = exercise["superset_id"]
					fancystring += "\n\nSuper Set "+str(the_superset_id+1)
				else:
					fancystring += "\n"+ss_string
			else:
				ss_string = " "
				fancystring += "\n"+ss_string
			fancystring += "\n"+ss_string+"    " + exercise["title"]
			
			has_weight = False
			has_reps = False
			has_distance = False
			has_duration = False
			
			# loop twice, first to decide format, then to write it out
			for exercise_set in exercise["sets"]:
				#fancystring += "\n        "+str(exercise_set["index"]+1)+":\t"
				if exercise_set["weight_kg"] != 0 and exercise_set["weight_kg"] != None:
					#fancystring += str(exercise_set["weight_kg"])+"kg\t"
					has_weight = True
				if exercise_set["reps"] != 0 and exercise_set["reps"] != None:
					#fancystring += str(exercise_set["reps"])+" reps\t"
					has_reps = True
				if exercise_set["distance_meters"] != 0 and exercise_set["distance_meters"] != None:
					#fancystring += str(exercise_set["distance_meters"])+"m\t"
					has_distance = True
				if exercise_set["duration_seconds"] != 0 and exercise_set["duration_seconds"] != None:
					#fancystring += str(exercise_set["duration_seconds"])+"s\t"
					has_duration = True
				#print(exercise_set)
			for exercise_set in exercise["sets"]:
				fancystring += "\n"+ss_string+"        "+str(exercise_set["index"]+1)+":\t"
				if has_weight:
					if self.weight_unit == "lbs":
						lb = round(exercise_set["weight_kg"]*2.20462262,2)
						if lb.is_integer():
							lb = int(lb)
						fancystring += str(lb)+"lb\t"
					else:
						fancystring += str(exercise_set["weight_kg"])+"kg\t"
				if has_reps:
					fancystring += str(exercise_set["reps"])+" reps\t"
				if has_distance:
					if exercise_set["distance_meters"] < 1000:
						fancystring += str(exercise_set["distance_meters"])+"m\t"
					else:
						fancystring += str(exercise_set["distance_meters"]/1000)+"km\t"
				if has_duration:
					#fancystring += str(datetime.timedelta(seconds=exercise_set["duration_seconds"]))+"\t"
					m, s = divmod(exercise_set["duration_seconds"], 60) 
					time_format = "{:02d}:{:02d}".format(m, s) 
					if m>59:
						h,m = divmod(m, 60) 
						time_format = "{:02d}:{:02d}:{:02d}".format(h, m, s) 
					fancystring += time_format+"\t"
				if len(exercise_set["personalRecords"])>0:
					fancystring += "*PR*"
		fancystring += "\n"
		
		fancystring += "\n     Social:  "+ str(workout["like_count"]) + " prop(s),  " + str(workout["comment_count"]) + " comment(s)\n"
		for comment in workout["comments"]:
			#print(comment)
			#fancystring += "\n     "+comment["username"]+": " +comment["comment"]
			stringlist = textwrap.wrap(comment["username"]+": " +comment["comment"], width=50,initial_indent="     " ,subsequent_indent="     ")
			for substring in stringlist:
				fancystring += "\n"+substring
			fancystring += "\n"
		
		fancystring += "\n"	
		return fancystring
	
	# returns true if workout json has filtered item in exercises or bodyparts
	def has_filtereditem(self, workoutjson, filteredItem):
		exercises = []
		bodyparts = []
		for exercise in workoutjson["exercises"]:
			title = exercise["title"]
			if title not in exercises:
				exercises.append(title)
			primarybodypart = exercise["muscle_group"]
			if primarybodypart not in bodyparts:
				bodyparts.append(primarybodypart)
			for other_bp in exercise["other_muscles"]:
				if other_bp not in bodyparts:
					bodyparts.append(other_bp)
		if filteredItem in exercises or filteredItem in bodyparts:
			return True
	
	# this is used when clicking on the calendar widget, returns the primary, secondary bodyparts in a workout
	def get_bodyparts(self, workoutjson):
	    bodyparts = []
	    other_bodyparts = []
	    for exercise in workoutjson["exercises"]:
	        bp = exercise["muscle_group"]
	        if bp not in bodyparts:
	            bodyparts.append(bp)
	        for other_bp in exercise["other_muscles"]:
	            if other_bp not in other_bodyparts:
	                other_bodyparts.append(other_bp)
	    #print(bodyparts)  
	    return bodyparts, other_bodyparts
		
	# this used for the filter combo box, returns the exercises and all bodyparts in a workout
	def get_exercisesandbodyparts(self, workoutjson):
		exercises = []
		bodyparts = []
		for exercise in workoutjson["exercises"]:
			title = exercise["title"]
			if title not in exercises:
				exercises.append(title)
			primarybodypart = exercise["muscle_group"]
			if primarybodypart not in bodyparts:
				bodyparts.append(primarybodypart)
			for other_bp in exercise["other_muscles"]:
				if other_bp not in bodyparts:
					bodyparts.append(other_bp)
		return exercises, bodyparts
	
	
	def feedScrollChanged(self, value): #https://doc.qt.io/qt-5/qabstractslider.html#valueChanged
		if value >= self.feedList.verticalScrollBar().maximum()-1000 and not self.feedloading: #if we're at the end
			self.feed_load_button()
	
	def reload_button(self):
		self.reloadbutton.setEnabled(False)
		worker = ReloadWorker()
		self.reloadworkemit = worker.emitter
		self.reloadworkemit.done.connect(self.on_reload_worker_done)
		self.pool.start(worker)
	
	def feed_reload_button(self):
		self.feed_last_index = 0
		self.feedList.clear()
		self.feed_load_button()
		#self.feed_load_button()
		#self.feed_load_button()
		
		# load the profile
		nextworker = ProfileWorker(self.current_user)
		self.nextworkeremit = nextworker.emitter
		self.nextworkeremit.done.connect(self.on_profile_worker_done)
		self.pool.start(nextworker)
		
	
	def feed_load_button(self):
		#self.feedreloadbutton.setEnabled(False)
		#self.feedloadbutton.setEnabled(False)
		start_index = self.feed_last_index + 0
		worker = MyFeedWorker(start_index, self.current_user)
		
		### The line below was creating a segmentation fault, found this: https://stackoverflow.com/questions/29123171/segmentation-fault-when-connecting-a-signal-and-a-slot
		#worker.emitter.done.connect(self.on_feed_worker_done)
		self.workemit = worker.emitter
		self.workemit.done.connect(self.on_feed_worker_done)
		self.feedloading = True
		self.pool.start(worker)
		
		
	
	@Slot(dict)
	def on_reload_worker_done(self):
		self.followList.clearSelection()
		self.friendList.clearSelection()
		self.squadList.clearSelection()
		self.do_update()
		
		
		self.reloadbutton.setEnabled(True)
		
	@Slot(dict)
	def on_profile_worker_done(self, the_data):
		print("all the work is done")
		#print(the_data)
		# try:
		the_string = ""
		if "full_name" in the_data.keys():
			the_string += the_data["full_name"]
		else:
			
			the_string += the_data["username"]
		if "description" in the_data.keys():
			the_string += "\n\n" + textwrap.fill(the_data["description"],50)
		the_string += "\n\nFollows You: " + str(the_data["is_followed_by_requester"])
		the_string += "\nYou Follow: " + str(the_data["following_status"]=="following")
		the_string += "\nWorkouts: " + str(the_data["workout_count"])
		the_string += "\nFollowers: " + str(the_data["follower_count"])
		the_string += "\nFollows: " + str(the_data["following_count"])
		#print(the_string)
		self.piclabel.setToolTip(the_string)
		# except:
			# None
		
		imageurl = the_data["profile_pic"]
		file_name = imageurl.split("/")[-1]
		img_folder = str(Path.home())+ "/.underthebar/temp/"
		
		if os.path.exists(img_folder+file_name):
			pixmap = QPixmap(img_folder+file_name)#.scaled(250,250)
			pixmap = self.makeProfileImage(pixmap)
			self.piclabel.setPixmap(pixmap)

	
	
	@Slot(dict)
	def on_feed_worker_done(self, returnjson):
		# modify the UI
		if returnjson != 304:
			#self.feedList.addItem(json.dumps(returnjson, indent=4, sort_keys=False))
			for workout in returnjson["data"]["workouts"]:
				#fancystring = workout["username"] + " - " + workout["name"]
				fancystring = workout["name"]
				workout_date = datetime.datetime.utcfromtimestamp(workout["start_time"])
				workout_date = workout_date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
				import platform
				if platform.system() == "Linux":
					fancystring += "\n" + workout_date.strftime("%a %b %-d, ") + str(len(workout["exercises"])) + " exercises"
				else:
					fancystring += "\n" + workout_date.strftime("%a %b %#d, ") + str(len(workout["exercises"])) + " exercises"
				
				
				the_superset_id = None
				ss_string = ""
				for exercise in workout["exercises"]:
					if exercise["superset_id"] != None:
						ss_string = "|"
						if exercise["superset_id"] != the_superset_id:
							the_superset_id = exercise["superset_id"]
							fancystring += "\n\nSuper Set "+str(the_superset_id+1)
						else:
							fancystring += "\n"+ss_string
					else:
						ss_string = ""
						fancystring += "\n"+ss_string
					fancystring += "\n"+ss_string+"    " + exercise["title"]
					
					has_weight = False
					has_reps = False
					has_distance = False
					has_duration = False
					
					# loop twice, first to decide format, then to write it out
					for exercise_set in exercise["sets"]:
						#fancystring += "\n        "+str(exercise_set["index"]+1)+":\t"
						if exercise_set["weight_kg"] != 0 and exercise_set["weight_kg"] != None:
							#fancystring += str(exercise_set["weight_kg"])+"kg\t"
							has_weight = True
						if exercise_set["reps"] != 0 and exercise_set["reps"] != None:
							#fancystring += str(exercise_set["reps"])+" reps\t"
							has_reps = True
						if exercise_set["distance_meters"] != 0 and exercise_set["distance_meters"] != None:
							#fancystring += str(exercise_set["distance_meters"])+"m\t"
							has_distance = True
						if exercise_set["duration_seconds"] != 0 and exercise_set["duration_seconds"] != None:
							#fancystring += str(exercise_set["duration_seconds"])+"s\t"
							has_duration = True
						#print(exercise_set)
					for exercise_set in exercise["sets"]:
						fancystring += "\n"+ss_string+"        "+str(exercise_set["index"]+1)+":\t"
						if has_weight:
							if self.weight_unit == "lbs":
								lb = round(exercise_set["weight_kg"]*2.20462262,2)
								if lb.is_integer():
									lb = int(lb)
								fancystring += str(lb)+"lbs\t"
							else:
								fancystring += str(round(exercise_set["weight_kg"],2))+"kg\t"
						if has_reps:
							fancystring += str(exercise_set["reps"])+" reps\t"
						if has_distance:
							if exercise_set["distance_meters"] < 1000:
								fancystring += str(exercise_set["distance_meters"])+"m\t"
							else:
								fancystring += str(exercise_set["distance_meters"]/1000)+"km\t"
						if has_duration:
							#fancystring += str(datetime.timedelta(seconds=exercise_set["duration_seconds"]))+"\t"
							m, s = divmod(exercise_set["duration_seconds"], 60) 
							time_format = "{:02d}:{:02d}".format(m, s) 
							if m>59:
								h,m = divmod(m, 60) 
								time_format = "{:02d}:{:02d}:{:02d}".format(h, m, s) 
							fancystring += time_format+"\t"
				fancystring += "\n"
				
				itemtoadd = QListWidgetItem(fancystring)
				itemtoadd.setToolTip(textwrap.fill(workout["description"],50))
				self.feedList.addItem(itemtoadd)
				#self.feedList.addItem(fancystring)
				#self.feedList.addItem("")
				
				

				
				
				item = QListWidgetItem()
				internalWidget = QWidget()
				internalLayout = QHBoxLayout()
				likebutton = QToolButton()
				likebutton.setIcon(self.loadIcon(self.script_folder+"/icons/thumbs-up-solid.svg"))
				likebutton.setCheckable(True)
				likebutton.setChecked(False)
				
				internalLayout.addWidget(likebutton)
				counterLabel = QLabel(str(workout["like_count"]))
				#counterLabel.setToolTip('<img src="https://b.thumbs.redditmedia.com/wjrOwbynl7LAxh4UACgPS4MBu3vjUXanM_NBsxixtys.jpg" width="100">')
				#counterLabel.setToolTip('<img src="test.jpg" width="400">')
				internalLayout.addWidget(counterLabel)
				internalLayout.addWidget(QLabel("prop(s)"))
				# add the workout pics
				for img_url in workout["image_urls"]:
					filename = img_url.split("/")[-1]
					img_folder = str(Path.home())+ "/.underthebar/temp/"
					#if os.path.exists(img_folder+filename): # following three lines were under this if, but now image might not be downloaded immediately
					pic_label = QLabel("Picture ")
					pic_label.setToolTip('<img src="'+img_folder+filename+'" width="400">')
					internalLayout.addWidget(pic_label)
				internalLayout.addStretch()
				internalLayout.setContentsMargins(0,0,0,0)
				internalWidget.setLayout(internalLayout)
				#item.setWidget(internalWidget)
				#item.setText("\n\"sick workout dude\" - a guy\n\n\"awesome!!!\" - a hot chick")
				#item.setText(str(workout["like_count"])+ " prop(s)")
				#item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
				#item.setCheckState(Qt.Unchecked)
				if workout["is_liked_by_user"]:
					likebutton.setChecked(True)
				item.setSizeHint(internalWidget.sizeHint())   
				self.feedList.addItem(item)
				self.feedList.setItemWidget(item, internalWidget)
				
				
				likebutton.clicked.connect(lambda *args, x=workout["id"], y=likebutton, z=counterLabel: self.like_button(args, x,y,z))
				#self.feed_last_index = workout["index"]
				self.feed_last_index +=1 # For other users its a workouts offset rather than the index
		
		#self.feedreloadbutton.setEnabled(True)
		#self.feedloadbutton.setEnabled(True)
		self.feedloading = False
	
	def like_button(self, checked, workout_id, button, label):
		#print(checked, workout_id, button.isChecked())
		if button.isChecked():
			worker = LikeWorker(label, workout_id)
			worker.emitter.done.connect(self.on_like_worker_done)
			self.pool.start(worker)	
		else:
			button.setChecked(True) # don't allow unliking

	@Slot(QLabel)
	def on_like_worker_done(self, the_label):
		if the_label != None:
			value = int(the_label.text()) + 1
			the_label.setText(str(value))
		
	def loadIcon(self, path):
	
		#QIcon qIcon;
		#qIcon.addFile(":/Icons/images/first.svg",QSize(32,32),QIcon::Normal,QIcon::On);
		#qIcon.addFile(":/Icons/images/second.svg",QSize(32,32),QIcon::Normal,QIcon::Off);

		
		img = QPixmap(path)
		qp = QPainter(img)
		qp.setCompositionMode(QPainter.CompositionMode_SourceIn)
		# You can enter any color you want here.
		qp.fillRect( img.rect(), QColor(self.palette().color(QPalette.Text)) ) 
		qp.end()
		#ic = QIcon(img)
		ic = QIcon()
		ic.addPixmap(img,QIcon.Normal,QIcon.On)
		qp = QPainter(img)
		qp.setCompositionMode(QPainter.CompositionMode_SourceIn)
		# You can enter any color you want here.
		qp.fillRect( img.rect(), QColor(self.palette().color(QPalette.AlternateBase)) ) 
		qp.end()
		#ic = QIcon(img)
		#ic = QIcon()
		ic.addPixmap(img,QIcon.Normal,QIcon.Off)
		return ic
			
	def makeProfileImage(self,pixmap):
		# Load image
		image = pixmap.toImage()

		# convert image to 32-bit ARGB (adds an alpha
		# channel ie transparency factor):
		image.convertToFormat(QImage.Format_ARGB32)

		# Crop image to a square:
		imgsize = min(image.width(), image.height())
		rect = QRect(
		(image.width() - imgsize) / 2,
		(image.height() - imgsize) / 2,
		imgsize,
		imgsize,
		)
		image = image.copy(rect)

		# Create the output image with the same dimensions 
		# and an alpha channel and make it completely transparent:
		out_img = QImage(imgsize, imgsize, QImage.Format_ARGB32)
		out_img.fill(Qt.transparent)

		# Create a texture brush and paint a circle 
		# with the original image onto the output image:
		brush = QBrush(image)

		# Paint the output image
		painter = QPainter(out_img)
		painter.setBrush(brush)

		# Don't draw an outline
		painter.setPen(Qt.NoPen)

		# drawing circle
		painter.drawEllipse(0, 0, imgsize, imgsize)


		# closing painter event
		painter.end()

		# Convert the image to a pixmap and rescale it. 
		pr = QWindow().devicePixelRatio()
		pm = QPixmap.fromImage(out_img)
		pm.setDevicePixelRatio(pr)
		#size *= pr
		pm = pm.scaled(300, 300, Qt.KeepAspectRatio, 
				       Qt.SmoothTransformation)
		return pm

class ReloadEmitter(QObject):
	# setting up custom signal
	done = Signal(dict)

class ReloadWorker(QRunnable):

	def __init__(self):
		super(ReloadWorker, self).__init__()

		self.emitter = ReloadEmitter()

	def run(self):
		#returnjson = hevy_api.feed_workouts_paged(self.start_from, user=self.feed_user)
		hevy_api.friends()
		hevy_api.cheer_squad()
		hevy_api.update_generic("suggested_users")
		self.emitter.done.emit(None)

class ProfileEmitter(QObject):
	# setting up custom signal
	done = Signal(dict)

class ProfileWorker(QRunnable):

	def __init__(self, the_user):
		super(ProfileWorker, self).__init__()
		self.the_user = the_user
		self.emitter = ProfileEmitter()

	def run(self):
		#returnjson = hevy_api.feed_workouts_paged(self.start_from, user=self.feed_user)
		the_data = hevy_api.get_user_profile(self.the_user)
		self.emitter.done.emit(the_data)

class MyEmitter(QObject):
	# setting up custom signal
	done = Signal(dict)

class MyFeedWorker(QRunnable):

	def __init__(self, start_from, feed_user):
		super(MyFeedWorker, self).__init__()

		self.start_from = start_from + 0
		self.feed_user = feed_user
		self.emitter = MyEmitter()

	def run(self):
		returnjson = hevy_api.feed_workouts_paged(self.start_from, user=self.feed_user)
		self.emitter.done.emit(returnjson)

class LikeEmitter(QObject):
	# setting up custom signal
	done = Signal(QLabel)

class LikeWorker(QRunnable):

	def __init__(self, the_label, workout_id):
		super(LikeWorker, self).__init__()

		self.the_label = the_label
		self.workout_id = workout_id
		self.emitter = LikeEmitter()

	def run(self):
		returnstatus = hevy_api.like_workout(self.workout_id, True)
		if returnstatus == 200:
			self.emitter.done.emit(self.the_label)
		else:
			self.emitter.done.emit(None)

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
	
	
	

	window = Social("red")
	window.do_update()
	#window.setFixedSize(800,600)
	window.resize(1200,800)
	window.show()

	app.exec_()
