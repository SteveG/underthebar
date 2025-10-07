#!/usr/bin/env python3
"""Under the Bar - Routines Page

Provides the routine viewer / editor. Think I'm intending this to be very basic, imagining a plain text editor working on json. haha.
"""

import sys
import json
import os
from pathlib import Path
import re

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QPlainTextEdit,
    QGroupBox,
    QMessageBox,
	QFileDialog
)
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Slot, Signal, QObject, QThreadPool, QRunnable

import hevy_api	
import garmin_translate
		
class Routines(QWidget):

	def __init__(self, color):
		super(Routines, self).__init__()
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
		self.routines_folder = user_folder + "/routines"
		if not os.path.exists(self.routines_folder):
			os.makedirs(self.routines_folder)
		
		
		#
		# on the left is a list routines
		#
		workoutslayout = QVBoxLayout()
		self.layout().addLayout(workoutslayout)
		#pagelayout.addStretch()

		
		self.workoutList = QListWidget()
		
		self.workoutList.setFixedWidth(300)
		self.workoutList.setSpacing(2)
		self.workoutList.setAlternatingRowColors(True)
		self.workoutList.currentRowChanged.connect(self.workoutListRowChanged)
		self.workoutList.itemDoubleClicked.connect(self.workoutDoubleClicked)
		
		
		#self.workoutList.installEventFilter(self)
		
		workoutslayout.addWidget(self.workoutList)
		
		#
		# Reload button below workout list   AND GARMIN TRANSLATE
		#
		self.reloadButton = QPushButton("Reload from Hevy")
		self.garminButton = QPushButton("Garmin")
		self.garminButton.setVisible(False)
		#self.reloadButton.clicked.connect(self.reloadButtonClicked)
		self.reloadButton.clicked.connect(lambda *args, x="routines_sync_batch": self.batch_button_pushed(x))
		self.garminButton.clicked.connect(self.garminButtonClicked)
		self.statusText = QLabel()
		sublayout = QHBoxLayout()
		sublayout.addWidget(self.reloadButton)
		sublayout.addWidget(self.statusText)
		sublayout.addWidget(self.garminButton)
		workoutslayout.addLayout(sublayout)
		
		#
		# front and centre is the routine text editor, such a silly idea
		#
		editorLayout = QVBoxLayout()
		self.routineEditor = QPlainTextEdit()
		#self.routineEditor.setFont(QFont("monospace"));
		
		editorLayout.addWidget(self.routineEditor)
		self.layout().addLayout(editorLayout)
		
		#
		# buttons under the editor
		#
		self.editorButtons = QGroupBox()
		self.editorButtons.setFlat(True)
		self.editorButtons.setStyleSheet("QGroupBox {border:0;padding:0;margin:0;}");
		
		buttonLayout = QHBoxLayout()
		buttonLayout.setContentsMargins(0,0,0,0)
		self.editorButtons.setLayout(buttonLayout)
		closeButton = QPushButton("Close Local")
		closeButton.clicked.connect(self.closeButtonClicked)
		discardButton = QPushButton("Discard Local")
		discardButton.clicked.connect(self.discardButtonClicked)
		self.pushButton = QPushButton("Push to Server")
		self.pushButton.clicked.connect(self.pushButtonClicked)
		deleteButton = QPushButton("Delete Routine")
		deleteButton.clicked.connect(self.deleteButtonClicked)
		buttonLayout.addWidget(closeButton)
		buttonLayout.addWidget(discardButton)
		buttonLayout.addWidget(self.pushButton)
		buttonLayout.addWidget(deleteButton)
		editorLayout.addWidget(self.editorButtons)
		
		self.editorButtons.setVisible(False)
		#self.editorButtons.setVisible(True)
		
		#
		# on the right is a list of exercises previously used
		#
		exerciseslayout = QVBoxLayout()
		self.layout().addLayout(exerciseslayout)
		
		self.exercisesList = QListWidget()
		self.exercisesList.setFixedWidth(300)
		self.exercisesList.setSpacing(2)
		self.exercisesList.setAlternatingRowColors(True)
		self.exercisesList.currentRowChanged.connect(self.exercisesListRowChanged)
		#self.exercisesList.itemDoubleClicked.connect(self.exercisesDoubleClicked)
		#self.exercisesList.addItem("--insert superset--\n")
		#self.exercisesList.item(0).setTextAlignment(Qt.AlignHCenter)
		exerciseslayout.addWidget(self.exercisesList)
		
		self.exercisesView = QPlainTextEdit()
		self.exercisesView.setFixedWidth(300)
		self.exercisesView.setFixedHeight(300)
		self.exercisesView.setReadOnly(True)
		exerciseslayout.addWidget(self.exercisesView)

	
		
		self.populate_lists()

		

		
		self.pool = QThreadPool()
		self.pool.setMaxThreadCount(5)
		

		self.initialised = True
		self.workoutList.setCurrentRow(0)
		

	def do_update(self):
		if not self.initialised:
			self.initialise()
	
	def populate_lists(self):
		#
		# Populate the list of routines with locally stored data, and exercises with all exercises in the routines
		#
		selected_row = self.workoutList.currentRow()
		
		self.workoutList.currentRowChanged.disconnect()
		self.workoutList.clear()
		self.exercisesList.clear()
		
		self.workoutList.addItem("--PLEASE EXPLAIN--\n")
		self.workoutList.item(0).setTextAlignment(Qt.AlignHCenter)
		self.workoutList.addItem("--new routine--\n")
		self.workoutList.item(1).setTextAlignment(Qt.AlignHCenter)
		
		
		fileslist = sorted(os.listdir(self.routines_folder), reverse=True)
		self.workoutList_files = []
		self.exercises = {}
		counter = 0
		
		# Attempt at sorting via folders / index
		folders = {}
		for filename in fileslist:
			match_workout = re.search('^routine_([A-Za-z0-9_-]+).json\Z',filename)
			if match_workout:
				with open(self.routines_folder+"/"+filename, 'r') as openfile:
					temp_data = json.load(openfile)
					routine_index = temp_data["index"]
					routine_folder = temp_data["folder_id"]
					if not routine_folder:
						routine_folder = 0
					
					#print(routine_index, routine_folder, match_workout[1])
					
					if routine_folder in folders.keys():
						folders[routine_folder].append([filename,routine_index])
					else:
						folders[routine_folder] = [[filename,routine_index],]
		newlist = []
		for folder_key in sorted(folders.keys()):
			indexes = {}
			for bodge_file in folders[folder_key]:
				if bodge_file[1] in indexes.keys():
					indexes[bodge_file[1]].append(bodge_file[0])
				else:
					indexes[bodge_file[1]] = [bodge_file[0],]
			for bodge_index in sorted(indexes.keys()):
				for super_bodge_index in indexes[bodge_index]:
					newlist.append(super_bodge_index)
		fileslist = newlist
		# End attempt at sorting via folders / index

		
		for filename in fileslist:
			match_workout = re.search('^routine_([A-Za-z0-9_-]+).json\Z',filename)
			if match_workout:
				with open(self.routines_folder+"/"+filename, 'r') as openfile:
					temp_data = json.load(openfile)
					routine_date = temp_data["updated_at"]
					routine_title = temp_data["title"]
					#workout_date = workout_date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

					if os.path.exists(self.routines_folder+"/modified/"+filename):
						self.workoutList.addItem("* "+temp_data["title"]+"\n    "+routine_date)
					else:
						self.workoutList.addItem(temp_data["title"]+"\n    "+routine_date)
					
					self.workoutList_files.append(filename)
			
					
					for exercise in temp_data["exercises"]:
						exercise_title = exercise["title"]
						exercise_json = "        "+json.dumps(self.jsonStripExercise(exercise), indent=4).replace("\n","\n        ")
						text_to_add = "From routine: "+routine_title+"\n\n"+exercise_json
						if exercise_title not in self.exercises.keys():
							#self.exercises[exercise_title] = routine_date + str(len(exercise["sets"])) + " sets"
							self.exercises[exercise_title] = text_to_add
						else:
							self.exercises[exercise_title] = self.exercises[exercise_title] + "\n\n" + text_to_add
			counter += 1
							
		for exercise_title in sorted(self.exercises.keys()):
			self.exercisesList.addItem(exercise_title+"\n")
			
		self.workoutList.currentRowChanged.connect(self.workoutListRowChanged)
		self.workoutList.setCurrentRow(selected_row)
	
		
	def workoutListRowChanged(self,row):
		print(self.workoutList.item(row).text(),"graph selected")
		try:
			self.routineEditor.textChanged.disconnect()
		except:
			pass
		
		selected_row = self.workoutList.currentRow()
		
		if selected_row ==0:
			self.routineEditor.setPlainText(\
"""
  This the new super fancy routine editor...

  Yes... it is a plain text editor 

        
        
  
  Hit "Reload from Hevy" on the bottom left to fetch the latest routine updates.
  
  Double click on a routine to enter edit mode (although "--new routine--" is always in edit mode).
  
  Once you make any sort of modification you now have two versions of the routine. Original and local.
  
  Routines that have a local version will be indicated by an asterix.
  
  "Close Local" will exit edit mode and display the original version. Double click to edit again.
  
  "Discard Local" will entirely discard any of your local edits and display the original version.
  
  "Push to Server" will submit your changes to Hevy. Follow with a "Reload from Hevy" to confirm.
  (local version is retained unchanged in case Hevy doesn't accept)
  
  "Delete Routine" will tell Hevy to delete the routine. (Applied locally after you "Reload from Hevy")
  
  
  
        
  The list on the right is all the exercises you currently have in your routines.
  
  Clicking on an exercise will reveal the raw data of how it's currently incorporated into your routines.
  
  The idea is to use that as a template when creating or modifying your routines.
  

  
  
  If you want easy, use the app or the website! Don't edit what you don't understand!
  
  Copy / paste from a spreadsheet program is something I have in mind with this. 
  
  Tip: Needs to be valid JSON. Make sure you have a comma between exercises.        
  
""")
			self.routineEditor.setReadOnly(True)
			self.editorButtons.setVisible(False)
			self.garminButton.setVisible(False)
		elif selected_row ==1:
			
			if os.path.exists(self.routines_folder+'/modified/newroutine.json'):
				with open(self.routines_folder+"/modified/newroutine.json", 'r') as openfile:
					self.routineEditor.setPlainText(openfile.read())
			else:
				defaultNew = \
"""{
    "routine": {
        "title": "All Hail lazy_steve",
        "exercises": [






        ],
        "index": -1,
        "folder_id": null,
        "program_id": null
    }
}"""
				self.routineEditor.setPlainText(defaultNew)
			self.routineEditor.document().setModified(False)
			self.routineEditor.setReadOnly(False)
			self.routineEditor.textChanged.connect(self.routineTextChanged)
			self.editorButtons.setVisible(True)
			self.garminButton.setVisible(False)
			
		else:
		
			print(self.workoutList_files[selected_row-2])
			filename = self.workoutList_files[selected_row-2]
			
			with open(self.routines_folder+"/"+filename, 'r') as openfile:
				temp_data = json.load(openfile)
				#
				temp_data = self.jsonStripRoutine(temp_data)
				self.routineEditor.setPlainText(json.dumps(temp_data,indent=4))
				
				self.routineEditor.document().setModified(False)
				self.routineEditor.setReadOnly(True)
				self.routineEditor.textChanged.connect(self.routineTextChanged)
				self.editorButtons.setVisible(False)
		
			## Show the garmin button
			
			if os.path.exists(self.routines_folder+'/garmin_translations.json'):
				self.garminButton.setVisible(True)
	#
	# Handle editing of the routine text editor
	#
	def routineTextChanged(self):
		if(self.routineEditor.document().isModified()):
			print("edits made")
			if not os.path.exists(self.routines_folder+'/modified'):
				os.makedirs(self.routines_folder+'/modified')
			
			selected_row = self.workoutList.currentRow()
			editedFile = None
			if selected_row ==0:
				print("this should be impossible...")
				return
			elif selected_row ==1:
				editedFile = self.routines_folder+"/modified/"+"newroutine.json"
			else:
				filename = self.workoutList_files[selected_row-2]
				editedFile = self.routines_folder+"/modified/"+filename
				oldText = self.workoutList.item(selected_row).text()
				if not oldText.startswith("* "):
					self.workoutList.item(selected_row).setText("* "+oldText)
			
			with open(editedFile, 'w') as openfile:
				openfile.write(self.routineEditor.toPlainText())
				openfile.close()

	def workoutDoubleClicked(self, item):
		selected_row = self.workoutList.currentRow()
		print(self.workoutList.item(selected_row).text()," to be edited")
		try:
			self.routineEditor.textChanged.disconnect()
		except:
			pass
		
		if selected_row ==0:
			return
		elif selected_row ==1:
			self.routineEditor.document().setModified(False)
			self.routineEditor.setReadOnly(False)
			self.routineEditor.textChanged.connect(self.routineTextChanged)
		
		else:
			print(self.workoutList_files[selected_row-2])
			filename = self.workoutList_files[selected_row-2]
			
			if os.path.exists(self.routines_folder+'/modified/'+filename):

			
				with open(self.routines_folder+"/modified/"+filename, 'r') as openfile:
					#temp_data = json.load(openfile)
					#
					#temp_data = self.jsonStripRoutine(temp_data)
					self.routineEditor.setPlainText(openfile.read())
				
			self.routineEditor.document().setModified(False)
			self.routineEditor.setReadOnly(False)
			self.routineEditor.textChanged.connect(self.routineTextChanged)
			self.editorButtons.setVisible(True)
		

	
	def exercisesListRowChanged(self,row):
		#print("exercisesList",row)
		print("selecting",self.exercisesList.currentItem().text().rstrip())
		the_exercise = self.exercisesList.currentItem().text().rstrip()
		self.exercisesView.setPlainText(self.exercises[the_exercise])
		
	def closeButtonClicked(self):
		print("closing")
		selected_row = self.workoutList.currentRow()
		if selected_row not in (0,1):
			self.workoutList.setCurrentRow(0)
			self.workoutList.setCurrentRow(selected_row)
	def discardButtonClicked(self):
		print("discarding...")
		selected_row = self.workoutList.currentRow()
		
		if selected_row == 0:
			return
		elif selected_row ==1:
			if os.path.exists(self.routines_folder+'/modified/newroutine.json'):
				os.remove(self.routines_folder+'/modified/newroutine.json')
			self.workoutList.setCurrentRow(0)
			self.workoutList.setCurrentRow(selected_row)
		else:
			filename = self.workoutList_files[selected_row-2]
			if os.path.exists(self.routines_folder+'/modified/'+filename):
				os.remove(self.routines_folder+'/modified/'+filename)
			self.workoutList.setCurrentRow(0)
			self.workoutList.setCurrentRow(selected_row)
			oldText = self.workoutList.item(selected_row).text()
			if oldText.startswith("* "):
				self.workoutList.item(selected_row).setText(oldText[2:])
		
	def pushButtonClicked(self):
		print("pushing to server")
		self.push_button_pushed()
		
	def deleteButtonClicked(self):
		print("deleting the routine")
		selected_row = self.workoutList.currentRow()
		if selected_row in (0,1):
			return
		
		messageBox = QMessageBox(self)
#		messageBox.setWindowFlags(Qt.FramelessWindowHint |Qt.WindowStaysOnTopHint)
#		messageBox.setText("WARNING\n\nThis will delete from Hevy entirely!!!")
#		messageBox.setIcon(QMessageBox.Critical)
#		messageBox.addButton(QMessageBox.Cancel)
#		messageBox.addButton(QMessageBox.Apply)
#		messageBox.setWindowModality(Qt.ApplicationModal)
#		print(messageBox.exec()==QMessageBox.Apply)
		reallyDelete = (messageBox.critical(self,"WARNING","This will delete from Hevy entirely!!!", QMessageBox.Cancel|QMessageBox.Apply)==QMessageBox.Apply)
		
		if reallyDelete:
			self.batch_button_pushed("delete_routine")
			
		
	def reloadButtonClicked(self):
		print("pull updates from server")
	
	
	def garminButtonClicked(self):
		print("garmin button was pressed")
		filename = self.workoutList_files[self.workoutList.currentRow()-2]
		destination = QFileDialog.getSaveFileName(self, "Save File","","CSV Files (*.csv)")[0]
		if destination != "":
			print("attempting translation of ", filename, destination)
			garmin_translate.do_translation(self.routines_folder+"/"+filename,destination,self.routines_folder+"/"+"garmin_translations.json")
	
	#
	# Takes a json object (dict etc) that has been imported from hevy file and strips to necessities
	#
	def jsonStripRoutine(self, json_object):
		r_keys = list(json_object.keys())
		for key in r_keys:
			if key not in ("title","folder_id","index","program_id","exercises"):
				del json_object[key]
			
		for exercise in json_object["exercises"]:
			exercise = self.jsonStripExercise(exercise)
			
		export_data = {"routine":json_object}
		return export_data
		
	# As above		
	def jsonStripExercise(self, json_object):
	
		
		exercise_keys = list(json_object.keys())
		for e_key in exercise_keys:
			if e_key not in ("exercise_template_id","title","notes","rest_seconds","sets","superset_id"):
				del json_object[e_key]
				
		for exercise_set in json_object["sets"]:
			s_keys = list(exercise_set.keys())
			for s_key in s_keys:
				if s_key not in ("index","indicator","weight_kg","reps","distance_meters","duration_seconds"):
					del exercise_set[s_key]
			#print(e_set)
			if exercise_set["weight_kg"] == None:
				del exercise_set["weight_kg"]
			if exercise_set["reps"] == None:
				del exercise_set["reps"]
			if exercise_set["distance_meters"] == None:
				del exercise_set["distance_meters"]
			if exercise_set["duration_seconds"] == None:
				del exercise_set["duration_seconds"]
		
		return json_object



	#
	# API Handling, can't remember how I came up with this, it seems shitty. Idea is to remove from UI thread
	#
	def batch_button_pushed(self, name):
		
		if name == "routines_sync_batch":
			print("start batch download",name)
			self.reloadButton.setEnabled(False)
			self.statusText.setText("updating...")
			
			worker = MyBatchWorker(name,0)
			worker.emitter.done.connect(self.on_batch_worker_done)
			self.pool.start(worker)
			
		elif name == "delete_routine":
			print("starting delete")
			self.statusText.setText("deleting...")
			selected_row = self.workoutList.currentRow()
			filename = self.workoutList_files[selected_row-2]
			if os.path.exists(self.routines_folder+'/'+filename):
				match_workout = re.search('^routine_([A-Za-z0-9_-]+).json\Z',filename)
				routine_id = match_workout[1]
				
				worker = MyBatchWorker(name,routine_id)
				worker.emitter.done.connect(self.on_batch_worker_done)
				self.pool.start(worker)
				
		
		
	@Slot(str,int,int)
	def on_batch_worker_done(self, worker, return_code, has_more):
		# modify the UI
		print("task completed:", worker, return_code, has_more)
		
		if has_more:
			if worker == "routines_sync_batch":
				self.statusText.setText("updating... more")
				
		else:
			if worker == "routines_sync_batch":
				self.reloadButton.setEnabled(True)
				self.statusText.setText("updated")
				self.populate_lists()
			elif worker == "delete_routine":
				self.statusText.setText("deleted (do a reload)")
				self.populate_lists()
				
	def push_button_pushed(self):
		print("start upload")
		
		
		selected_row = self.workoutList.currentRow()
		if selected_row == 0:
			return
		elif selected_row ==1:
			#return # haven't handled yet
			
			if os.path.exists(self.routines_folder+'/modified/newroutine.json'):
				with open(self.routines_folder+'/modified/newroutine.json', 'r') as openfile:
					try:
						routine_json = json.load(openfile)
					except:
						self.statusText.setText("fail: not valid json")
						return
				
					worker = MyUploadWorker(routine_json)
					worker.emitter.done.connect(self.on_push_worker_done)
					self.statusText.setText("Uploading")
					self.pushButton.setEnabled(False)
					self.pool.start(worker)
			else:
				self.statusText.setText("Fail: no modified file")
			
		else:
			filename = self.workoutList_files[selected_row-2]
			if os.path.exists(self.routines_folder+'/modified/'+filename):
				match_workout = re.search('^routine_([A-Za-z0-9_-]+).json\Z',filename)
				routine_id = match_workout[1]
				with open(self.routines_folder+'/modified/'+filename, 'r') as openfile:
					try:
						routine_json = json.load(openfile)
					except:
						self.statusText.setText("fail: not valid json")
						return
				
					worker = MyUploadWorker(routine_json,routine_id=routine_id)
					worker.emitter.done.connect(self.on_push_worker_done)
					self.statusText.setText("Uploading")
					self.pool.start(worker)
				
				#os.remove(self.routines_folder+'/modified/'+filename)
			else:
				self.statusText.setText("Fail: no modified file")
			
		
	@Slot(str,int,int)
	def on_push_worker_done(self, routine_id, routine_json, status):
		# modify the UI
		print("task completed:", routine_id, status)
		self.statusText.setText("Uploaded (do a reload)")
		self.pushButton.setEnabled(True)
		return


class MyEmitter(QObject):
	# setting up custom signal
	done = Signal(str,int,int)

class MyUploadWorker(QRunnable):

	def __init__(self, the_json, routine_id=None):
		super(MyUploadWorker, self).__init__()
		self.routine_id = routine_id
		self.the_json = the_json
		self.emitter = MyEmitter()

	@Slot()
	def run(self):

		status = hevy_api.put_routine(self.the_json, routine_id = self.routine_id)
		self.emitter.done.emit(str(self.routine_id),self.the_json,status)
		
		
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
				if self.name == "routines_sync_batch":
					status = hevy_api.routines_sync_batch()
				elif self.name == "delete_routine":
					status = hevy_api.delete_routine(self.startIndex)
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
	
	
	

	window = Routines("red")
	window.do_update()
	#window.setFixedSize(800,600)
	window.resize(1200,800)
	window.show()

	app.exec_()
