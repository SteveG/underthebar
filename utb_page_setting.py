#!/usr/bin/env python3
"""Under the Bar - Settings Page

This file provides the settings page for application, currently mainly provides routines to fetch API data.
"""

import sys
import json
import os
from pathlib import Path

from PySide2.QtCore import QSize, Qt
from PySide2.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QWidget,
)
from PySide2.QtGui import QPalette, QColor
from PySide2.QtGui import QIcon, QPixmap, QPainter
from PySide2.QtCore import Slot, Signal, QObject, QThreadPool, QRunnable

import hevy_api	

#
# This view provides means to adjust settings and/or interact with the Hevy API
#		
class Setting(QWidget):

	def __init__(self, color):
		super(Setting, self).__init__()
		home_folder = str(Path.home())
		utb_folder = home_folder + "/.underthebar"
		self.script_folder = os.path.split(os.path.abspath(__file__))[0]
		
		
		session_data = {}
		if os.path.exists(utb_folder+"/session.json"):	
			with open(utb_folder+"/session.json", 'r') as file:
				session_data = json.load(file)
		else:
			return 403
		user_folder = utb_folder + "/user_" + session_data["user-id"]	
		if not os.path.exists(user_folder):
			os.makedirs(user_folder)
			os.makedirs(user_folder+"/workouts")
			os.makedirs(user_folder+"/routines")
		
		self.user_folder = utb_folder + "/user_" + session_data["user-id"]	
		
#		account_data = None
#		if os.path.exists(user_folder+"/account.json"):	
#			with open(user_folder+"/account.json", 'r') as file:
#				account_data = json.load(file)
		workoutcount_data = None
		if os.path.exists(user_folder+"/workout_count.json"):	
			with open(user_folder+"/workout_count.json", 'r') as file:
				workoutcount_data = json.load(file)
		else:
			workoutcount_data = {"data": {"workout_count": 0}}
		
		pagelayout = QVBoxLayout()
		toplayout = QHBoxLayout()
		pagelayout.addLayout(toplayout)
		pagelayout.addStretch()

		toplayout.addStretch()
	
	
		detailslayout = QVBoxLayout()
		#detailslayout.addWidget(QLabel("Details"))
		detailsgrid = QGridLayout()
		
		
		
		self.apiCallable = ["account","body_measurements","set_personal_records","user_preferences","user_subscription","workout_count",]
		self.apiCallable_dict = {}
		self.apiCallable_button = []
		self.apiCallable_stateLabel = []
		for btnID in range(len(self.apiCallable)):
			self.apiCallable_dict[self.apiCallable[btnID]] = btnID
		
			thelabel = QLabel(self.apiCallable[btnID])
			thelabel.setFixedWidth(200)
			detailsgrid.addWidget(thelabel, btnID,0)
		
			btn = QPushButton()

			btn.setIcon(self.loadIcon(self.script_folder+"/icons/cloud-arrow-down-solid.svg"))
			btn.setIconSize(QSize(24,24))

			btn.clicked.connect(lambda *args, x=btnID: self.update_button_pushed(x))
			self.apiCallable_button.append(btn)
			detailsgrid.addWidget(btn,btnID,1)
			
			stateLabel = QLabel()
			stateLabel.setFixedWidth(200)
			self.apiCallable_stateLabel.append(stateLabel)
			detailsgrid.addWidget(stateLabel,btnID,2)
		
		detailslayout.addLayout(detailsgrid)
			
		workoutSyncLabel = QLabel("\nWorkout Synchronisation")
		detailslayout.addWidget(workoutSyncLabel)
		localWorkoutCount = len(os.listdir(user_folder+"/workouts"))
		workoutsyncgrid = QGridLayout()
		self.localworkoutsLabel = QLabel("Local Workouts: "+str(localWorkoutCount))
		detailslayout.addWidget(self.localworkoutsLabel)#,0,0)
		self.remoteworkoutsLabel = QLabel("Remote Workouts: "+str(workoutcount_data["data"]["workout_count"]))
		detailslayout.addWidget(self.remoteworkoutsLabel)#,0,2)
		
		#Batch download
		workouts_batch_label = QLabel("workouts_batch")
		workouts_batch_label.setFixedWidth(200)
		workoutsyncgrid.addWidget(workouts_batch_label, 1,0)
		self.workoutsyncbtn = QPushButton()
		self.workoutsyncbtn.setIcon(self.loadIcon(self.script_folder+"/icons/cloud-arrow-down-solid.svg"))
		self.workoutsyncbtn.setIconSize(QSize(24,24))
		#self.workoutsyncbtn.clicked.connect(self.batch_button_pushed)
		self.workoutsyncbtn.clicked.connect(lambda *args, x="workouts_batch": self.batch_button_pushed(x))
		workoutsyncgrid.addWidget(self.workoutsyncbtn,1,1)
		self.workoutsyncstateLabel = QLabel("Use for bulk downloads")
		self.workoutsyncstateLabel.setFixedWidth(200)
		workoutsyncgrid.addWidget(self.workoutsyncstateLabel,1,2)
		
		#Workout Sync Batch download
		workouts_sync_batch_label = QLabel("workouts_sync_batch")
		workouts_sync_batch_label.setFixedWidth(200)
		workoutsyncgrid.addWidget(workouts_sync_batch_label, 2,0)
		self.workoutsyncbatchbtn = QPushButton()
		self.workoutsyncbatchbtn.setIcon(self.loadIcon(self.script_folder+"/icons/cloud-arrow-down-solid.svg"))
		self.workoutsyncbatchbtn.setIconSize(QSize(24,24))
		#self.workoutsyncbatchbtn.clicked.connect(self.batch_button_pushed)
		self.workoutsyncbatchbtn.clicked.connect(lambda *args, x="workouts_sync_batch": self.batch_button_pushed(x))
		workoutsyncgrid.addWidget(self.workoutsyncbatchbtn,2,1)
		self.workoutsyncbatchstateLabel = QLabel("Use for latest updates")
		self.workoutsyncbatchstateLabel.setFixedWidth(200)
		workoutsyncgrid.addWidget(self.workoutsyncbatchstateLabel,2,2)
		
		
		
		
		# Log out and quit button
		log_out_label = QLabel("Logout and Quit")
		log_out_label.setFixedWidth(200)
		workoutsyncgrid.addWidget(log_out_label, 4,0)
		self.log_out_button = QPushButton("Logout\nand Quit")
		self.log_out_button.clicked.connect(self.log_out_quit)
		workoutsyncgrid.addWidget(self.log_out_button,4,1)
		
		detailslayout.addLayout(workoutsyncgrid)
		#detailslayout.addStretch()
		toplayout.addLayout(detailslayout)
		toplayout.addStretch()

		self.setLayout(pagelayout)		
		
		self.pool = QThreadPool()
		self.pool.setMaxThreadCount(5)
		#print("Multithreading with maximum %d threads" % self.pool.maxThreadCount())
	
	def log_out_quit(self):
		print("Quitting...")
		hevy_api.logout()
		sys.exit()
	
	def update_button_pushed(self, button_id):
	
		self.apiCallable_button[button_id].setIcon(self.loadIcon(self.script_folder+"/icons/spinner-solid.svg"))
		self.apiCallable_button[button_id].setIconSize(QSize(24,24))
		self.apiCallable_button[button_id].setEnabled(False)
		self.apiCallable_stateLabel[button_id].setText("updating...")
		
		#self.launch_threadpool()
		worker = MyWorker(self.apiCallable[button_id],button_id)
		worker.emitter.done.connect(self.on_worker_done)
		self.pool.start(worker)

	def batch_button_pushed(self, name):
		print("start batch download",name)
		if name == "workouts_batch":
			self.workoutsyncbtn.setIcon(self.loadIcon(self.script_folder+"/icons/spinner-solid.svg"))
			self.workoutsyncbtn.setIconSize(QSize(24,24))
			self.workoutsyncbtn.setEnabled(False)
			self.workoutsyncbatchbtn.setEnabled(False)
			self.workoutsyncstateLabel.setText("updating...")
		elif name == "workouts_sync_batch":
			self.workoutsyncbatchbtn.setIcon(self.loadIcon(self.script_folder+"/icons/spinner-solid.svg"))
			self.workoutsyncbatchbtn.setIconSize(QSize(24,24))
			self.workoutsyncbatchbtn.setEnabled(False)
			self.workoutsyncbtn.setEnabled(False)
			self.workoutsyncbatchstateLabel.setText("updating...")
		#self.launch_threadpool()
		worker = MyBatchWorker(name,0)
		worker.emitter.done.connect(self.on_batch_worker_done)
		self.pool.start(worker)
		#QThreadPool.globalInstance().start(worker)

	@Slot(str,int,int)
	def on_worker_done(self, worker, orig_id, status):
		# modify the UI
		print("task completed:", worker)
		
		self.apiCallable_button[orig_id].setIcon(self.loadIcon(self.script_folder+"/icons/cloud-arrow-down-solid.svg"))
		self.apiCallable_button[orig_id].setIconSize(QSize(24,24))
		self.apiCallable_button[orig_id].setEnabled(True)
		
		if status == 200:
			self.apiCallable_stateLabel[orig_id].setText("updated")
			
			if worker == "workout_count":
				if os.path.exists(self.user_folder+"/workout_count.json"):	
					with open(self.user_folder+"/workout_count.json", 'r') as file:
						workoutcount_data = json.load(file)
						self.remoteworkoutsLabel.setText("Remote Workouts: "+str(workoutcount_data["data"]["workout_count"]))
		elif status == 304:
			self.apiCallable_stateLabel[orig_id].setText("no update")
			
		
	
	@Slot(str,int,int)
	def on_batch_worker_done(self, worker, return_code, has_more):
		# modify the UI
		print("task completed:", worker, return_code, has_more)
		
		localWorkoutCount = len(os.listdir(self.user_folder+"/workouts"))
		self.localworkoutsLabel.setText("Local Workouts: "+str(localWorkoutCount))
		
		if has_more:
			if worker == "workouts_batch":
				self.workoutsyncstateLabel.setText("updating... more")
			elif worker == "workouts_sync_batch":
				self.workoutsyncbatchstateLabel.setText("updating... more")
				
		else:
			if worker == "workouts_batch":
				self.workoutsyncbtn.setIcon(self.loadIcon(self.script_folder+"/icons/cloud-arrow-down-solid.svg"))
				self.workoutsyncbtn.setIconSize(QSize(24,24))
				self.workoutsyncbtn.setEnabled(True)
				self.workoutsyncbatchbtn.setEnabled(True)
				self.workoutsyncstateLabel.setText("updated")
			elif worker == "workouts_sync_batch":
				self.workoutsyncbatchbtn.setIcon(self.loadIcon(self.script_folder+"/icons/cloud-arrow-down-solid.svg"))
				self.workoutsyncbatchbtn.setIconSize(QSize(24,24))
				self.workoutsyncbtn.setEnabled(True)
				self.workoutsyncbatchbtn.setEnabled(True)
				self.workoutsyncbatchstateLabel.setText("updated")
		

		

	def loadIcon(self, path):
		img = QPixmap(path)
		qp = QPainter(img)
		qp.setCompositionMode(QPainter.CompositionMode_SourceIn)
		# You can enter any color you want here.
		qp.fillRect( img.rect(), QColor(self.palette().color(QPalette.Text)) ) 
		qp.end()
		ic = QIcon(img)
		return ic


class MyEmitter(QObject):
	# setting up custom signal
	done = Signal(str,int,int)

class MyWorker(QRunnable):

	def __init__(self, name, orig_id):
		super(MyWorker, self).__init__()
		self.name = name
		self.origId = orig_id
		self.emitter = MyEmitter()

	def run(self):
		#print(f"{self.name} api caller starting to run.")
		status = hevy_api.update_generic(self.name)
		#print(f"{self.name} api caller finishing up -> emit signal.")
		self.emitter.done.emit(str(self.name),self.origId,status)
		
		
class MyBatchWorker(QRunnable):

	def __init__(self, name, startIndex):
		super(MyBatchWorker, self).__init__()
		self.name = name
		self.startIndex = startIndex
		self.emitter = MyEmitter()
	
	@Slot()
	def run(self):
		#print(f"{self.name} api caller starting to run.")
		keepGoing = True
		while keepGoing:
			status = (200, False)
			try:
				if self.name == "workouts_batch":
					status = hevy_api.batch_download()
				elif self.name == "workouts_sync_batch":
					status = hevy_api.workouts_sync_batch()
			except:
				self.emitter.done.emit(str(self.name),0,False)
				break
			self.emitter.done.emit(str(self.name),status[0],status[1])
			keepGoing = status[1]
		#print(f"{self.name} api caller finishing up -> emit signal.")
		#self.emitter.done.emit(str(self.name),status[0],status[1])

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
	
	
	

	window = Setting("red")
	#window.setFixedSize(800,600)
	window.resize(1200,800)
	window.show()

	app.exec_()
