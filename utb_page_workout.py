#!/usr/bin/env python3
"""Under the Bar - Workout Page

Provides the workout construction page for the application. Doesn't work yet, experimental.
"""

import sys
import json
import os
from pathlib import Path
import re
import datetime

from PySide2.QtCore import QSize, Qt, QRect, QEvent
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide2.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QStackedLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QLayout,
    QAbstractScrollArea,
    QSizePolicy,
    QStackedWidget,
    QMenu,
    QAction
)
from PySide2.QtGui import QPalette, QColor, QWindow, QDoubleValidator
from PySide2.QtGui import QIcon, QPixmap,QRegion, QImage, QBrush, QPainter
from PySide2 import QtSvg
	
		
class Workout(QWidget):

	def __init__(self, color):
		super(Workout, self).__init__()
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
		workouts_folder = user_folder + "/workouts"
		account_data = None
		if os.path.exists(user_folder+"/account.json"):	
			with open(user_folder+"/account.json", 'r') as file:
				account_data = json.load(file)
		workoutcount_data = None
		if os.path.exists(user_folder+"/workout_count.json"):	
			with open(user_folder+"/workout_count.json", 'r') as file:
				workoutcount_data = json.load(file)
		
		
		#
		# on the left is a list of workouts or saved routines
		#
		workoutslayout = QVBoxLayout()
		self.layout().addLayout(workoutslayout)
		#pagelayout.addStretch()

		
		self.workoutList = QListWidget()
		self.workoutList.setFixedWidth(200)
		self.workoutList.setSpacing(2)
		self.workoutList.setAlternatingRowColors(True)
		self.workoutList.currentRowChanged.connect(self.workoutListRowChanged)
		self.workoutList.addItem("--edit workout--\n")
		self.workoutList.item(0).setTextAlignment(Qt.AlignHCenter)
		self.workoutList.installEventFilter(self)
		
		workoutslayout.addWidget(self.workoutList)
		
		#
		# after the workout list is an exercises list
		#
		exerciseslayout = QVBoxLayout()
		self.layout().addLayout(exerciseslayout)
		
		self.exercisesList = QListWidget()
		self.exercisesList.setFixedWidth(200)
		self.exercisesList.setSpacing(2)
		self.exercisesList.setAlternatingRowColors(True)
		self.exercisesList.currentRowChanged.connect(self.exercisesListRowChanged)
		self.exercisesList.itemDoubleClicked.connect(self.exercisesDoubleClicked)
		self.exercisesList.addItem("--insert superset--\n")
		self.exercisesList.item(0).setTextAlignment(Qt.AlignHCenter)
		exerciseslayout.addWidget(self.exercisesList)
		
		

		#
		# on the right is stacked widget that can switch between workout editor, workout viewer, exercise information viewer
		#
		self.stackWidget = QStackedWidget()
		
		self.workoutEditor = QWidget()
		self.workoutEditor.setLayout(QHBoxLayout())
		self.stackWidget.addWidget(self.workoutEditor)
		
		self.layout().addWidget(self.stackWidget)
		
		
		
		#
		# the workout editor, consists of a list of exercises on the left, and set builders on the right
		#
		self.setgroupList = QListWidget()
		self.setgroupList.setFixedWidth(200)
		self.setgroupList.setSpacing(0)
		self.setgroupList.setAlternatingRowColors(True)
		#self.exercisesList.currentRowChanged.connect(self.exercisesListRowChanged)
		#self.setgroupList.addItem("Exercise \nA")
		#self.setgroupList.addItem("Exercise \nB")
		#self.setgroupList.addItem("Exercise \nC")
		self.setgroupList.setDragDropMode(QAbstractItemView.InternalMove);
		#self.setgroupList.setSelectionMode(QAbstractItemView.NoSelection)
		#self.setgroupList.setFocusPolicy(Qt.NoFocus);
		#self.setgroupList.keyPressEvent.connect(self.setgroupKeyPress)
		#self.layout().addWidget(self.setgroupList)
		self.workoutEditor.layout().addWidget(self.setgroupList)
		
		
		
		fileslist = sorted(os.listdir(workouts_folder), reverse=True)
		self.workoutList_files = []
		self.exercises = {}
		counter = 0
		for file in fileslist[:90]:
			match_workout = re.search('^workout_([A-Za-z0-9_-]+).json\Z',file)
			if match_workout:
				with open(workouts_folder+"/"+file, 'r') as file:
					temp_data = json.load(file)
					workout_date = datetime.datetime.utcfromtimestamp(temp_data["start_time"])
					workout_date = workout_date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
					if counter < 20:
						temp_index = temp_data["index"]
						self.workoutList.addItem(temp_data["name"]+"\n"+workout_date.strftime("%a %b %-d, %Y, %-I%P"))
						
						self.workoutList_files.append(file)
					
					for exercise in temp_data["exercises"]:
						exercise_title = exercise["title"]
						if exercise_title == "Standing Calf Raise":
							print(workout_date)
						if exercise_title not in self.exercises.keys():
							self.exercises[exercise_title] = workout_date.strftime("%a %b %-d, ") + str(len(exercise["sets"])) + " sets"
			counter += 1
							
		for exercise_title in sorted(self.exercises.keys()):
			self.exercisesList.addItem(exercise_title+"\n"+self.exercises[exercise_title])
		
		
		
		self.setgroupList.model().rowsMoved.connect(self.setgroupRowsMoved)
		self.setgroupList.model().rowsInserted.connect(self.row_insert)
		self.setgroupList.model().rowsRemoved.connect(self.row_remove)
		
		#
		# The workout Edit area
		#
		self.workoutEditLayout = QVBoxLayout()
		funList = QListWidget()
		funList.setSelectionMode(QAbstractItemView.NoSelection)
		funList.setFocusPolicy(Qt.NoFocus);
		#funList.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents);
		#funList.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding);
		self.workoutEditLayout.addWidget(funList)
		#self.workoutEditLayout.addStretch()
		
		itemN = QListWidgetItem() 
		#Create test list widget
		widget = QWidget()
		widgetText =  QLabel("I love PyQt!")
		widgetButton =  QPushButton("Add Set")
		widgetLayout = QVBoxLayout()
		widgetLayout.setContentsMargins(0,0,0,0)
		widgetLayout.addWidget(QLabel("Bench Press (Barbell)"))
		#widgetLayout.addWidget(widgetText)
		#setList = QListWidget()
		#setList.addItem("fish")
		#setList.addItem("dog")
		#widgetLayout.addWidget(setList)
		edit2 = QLineEdit()
		edit2.setPlaceholderText("20.0")
		spin2 = QDoubleSpinBox()
		spin2.setValue(50.0)
		spin2.setRange(0,1000)
		spin2.setSingleStep(0.5)
		
		setTable = QTableWidget(5,6)
		setTable.horizontalHeader().setMinimumSectionSize(1)
		setTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);
		setTable.verticalHeader().setMinimumSectionSize(1)
		setTable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch);
		setTable.setItem(1,1,QTableWidgetItem())
		setTable.setCellWidget(1,1,widgetText)
		setTable.setCellWidget(1,2,edit2)
		setTable.setCellWidget(1,3,spin2)
		setTable.setHorizontalHeaderLabels(('Previous 3','Previous 2','Previous 1','Weight','Reps','Completed'))
		setTable.setSelectionMode(QAbstractItemView.NoSelection)
		setTable.setFocusPolicy(Qt.NoFocus);
		widgetLayout.addWidget(setTable)
		#edit = QLineEdit()
		#edit.setPlaceholderText("fishing")
		#edit.setValidator(QDoubleValidator(0, 1000, 5, edit));
		#widgetLayout.addWidget(edit)
		
		widgetLayout.addWidget(widgetButton)


		#widgetLayout.setSizeConstraint(QLayout.SetFixedSize)
		widget.setLayout(widgetLayout)  
		itemN.setSizeHint(widget.sizeHint())    

		#Add widget to QListWidget funList
		funList.addItem(itemN)
		funList.setItemWidget(itemN, widget)
		funList.setFixedHeight(funList.sizeHintForRow(0) * funList.count() + 2 * funList.frameWidth())
		
		
		script_folder = os.path.split(os.path.abspath(__file__))[0]
		svgWidget = QtSvg.QSvgWidget(script_folder+"/icons/chart-line-solid.svg")
		svgWidget.resize(500,500)
		
		
		self.workoutEditLayout.addWidget(svgWidget)
		#self.layout().addLayout(self.workoutEditLayout)
		self.workoutEditor.layout().addLayout(self.workoutEditLayout)
		
		self.superset_count = 0
		self.initialised = True
		self.workoutList.setCurrentRow(0)
		
		#self.keyPressEvent().connect(self.on_key)

	def do_update(self):
		if not self.initialised:
			self.initialise()
	
	
	def eventFilter(self, source, event):
		if (event.type() == QEvent.ContextMenu and source is self.workoutList):
			menu = QMenu()
			open_window_1 = QAction("Open Window 1")
			open_window_2 = QAction("Open Window 2")
			menu.addAction(open_window_1)
			menu.addAction(open_window_2)
			menu_click = menu.exec_(event.globalPos())
			
			try:
				item = source.itemAt(event.pos())
			except Exception as e:
				print(f"No item selected {e}")

			if menu_click == open_window_1 :
				print("Opening Window 1...")
				print(item.text())
				# Your code here
			if menu_click == open_window_2 :
				print("Opening Window 2...")
				print(item.text())
				# Your code here
			return True
		return super(Workout, self).eventFilter(source, event)
	
	
	
	
	
	def row_insert(self, parent, start, end):
		print("exercise inserted",start, end)
		for x in range(start,end+1):
			print(self.setgroupList.item(x).text().splitlines()[0])
			
	
	def row_remove(self, parent, start, end):
		print("exercise removed",start,end)
		for x in range(start,end+1):
			print("removed",x)	
			
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Delete:
			if self.setgroupList.hasFocus():
				self.setgroupList.takeItem(self.setgroupList.currentIndex().row())
	
	def setgroupRowsMoved(self, sourceParent, sourceStart, sourceEnd, destinationParent, destinationRow):
		#print("sourcestart",sourceStart,"sourceend",sourceEnd,"destination",destinationRow)
		
		movedItemIndex = None
		if sourceStart < destinationRow:
			#print("End position", destinationRow -1)
			movedItemIndex = destinationRow -1
#			self.setgroupList.blockSignals(True)
#			currentItem = self.setgroupList.takeItem(destinationRow -1)
#			self.setgroupList.insertItem(sourceStart, currentItem)
#			self.setgroupList.setCurrentRow( sourceStart )
#			self.setgroupList.blockSignals(False)
		elif sourceStart > destinationRow:
			#print("End position", destinationRow)
			movedItemIndex = destinationRow
			
		movedItemText = self.setgroupList.item(movedItemIndex).text()
		
		match_footer = re.search('SUPERSET ([0-9]+) FOOTER',movedItemText)
		if match_footer:
			print("its a superset footer!!!! Superset:",match_footer[1])
			superset_id =  match_footer[1]
			for x in range(movedItemIndex,sourceStart+1): # if moved up
				if self.setgroupList.item(x).text() == "SUPERSET "+str(superset_id)+ " HEADER":
					print("found matching header at: ", x)
					if x > movedItemIndex:	# don't let user move footer up above the header
						self.setgroupList.blockSignals(True)
						currentItem = self.setgroupList.takeItem(movedItemIndex)
						self.setgroupList.insertItem(x, currentItem)
						self.setgroupList.setCurrentRow( x )
						self.setgroupList.blockSignals(False)
						break
			for x in range(sourceStart,movedItemIndex): # if moved down
				
				match_another = re.search('SUPERSET ([0-9]+) .+', self.setgroupList.item(x).text()) # don't let user move footer down into other supersets
				if match_another:
					print("conflict!!!")
					self.setgroupList.blockSignals(True)
					currentItem = self.setgroupList.takeItem(movedItemIndex)
					self.setgroupList.insertItem(x, currentItem)
					self.setgroupList.setCurrentRow( x )
					self.setgroupList.blockSignals(False)
					break
					
					
		match_header = re.search('SUPERSET ([0-9]+) HEADER',movedItemText)
		if match_header:
			print("its a superset header!!!! Superset:",match_header[1])
			superset_id =  match_header[1]
			counter_superset_headfoot = 0
			first_superset_headfoot = None
			last_superset_headfoot = 0
			for x in range(movedItemIndex+1,self.setgroupList.count()):
				match_another = re.search('SUPERSET ([0-9]+) .+', self.setgroupList.item(x).text())
				if match_another:
					if first_superset_headfoot == None:
						first_superset_headfoot = x
					last_superset_headfoot = x
					counter_superset_headfoot += 1
			print("movedItemIndex",movedItemIndex)
			if (movedItemIndex<sourceStart and counter_superset_headfoot%2==0) or (movedItemIndex>sourceStart and counter_superset_headfoot%2 == 1): # moved inside another superset
				print("moved into another superset")
				self.setgroupList.blockSignals(True)
				currentItem = self.setgroupList.takeItem(movedItemIndex)
				self.setgroupList.insertItem(first_superset_headfoot, currentItem)
				self.setgroupList.setCurrentRow( first_superset_headfoot )
				self.setgroupList.blockSignals(False)
				movedItemIndex = first_superset_headfoot
			#print("validity not odd",counter_superset_headfoot,first_superset_headfoot,last_superset_headfoot)
			
			for x in range(sourceStart,self.setgroupList.count()):
				if self.setgroupList.item(x).text() == "SUPERSET "+str(superset_id)+ " FOOTER":
					print("found matching footer at: ", x, movedItemIndex)
					if movedItemIndex> sourceStart and movedItemIndex <= x+1: # its been moved down into itself, just undo
						print("moved down into itself", movedItemIndex, sourceStart)
						self.setgroupList.blockSignals(True)
						currentItem = self.setgroupList.takeItem(movedItemIndex)
						self.setgroupList.insertItem(sourceStart, currentItem)
						self.setgroupList.setCurrentRow( sourceStart )
						self.setgroupList.blockSignals(False)
						movedItemIndex = sourceStart
						break
					
					# move the whole superset
					self.setgroupList.blockSignals(True)	
					print("moving children:",x-sourceStart+1)
					moveselection =0
					for y in range(x-sourceStart+1):
						print("moving blocks",y)
						if sourceStart < movedItemIndex:
							print("moving:",self.setgroupList.item(sourceStart).text())
							currentItem = self.setgroupList.takeItem(sourceStart)
							self.setgroupList.insertItem(movedItemIndex, currentItem)
							moveselection +=1
						if sourceStart > movedItemIndex:
							currentItem = self.setgroupList.takeItem(sourceStart+y+1)
							self.setgroupList.insertItem(movedItemIndex+y+1, currentItem)

					
					self.setgroupList.setCurrentRow( movedItemIndex -moveselection)		
					self.setgroupList.blockSignals(False)
					break
		
		
		#sourceText = self.setgroupList.item(sourceStart).text()
		#destination = self.setgroupList.item(destinationRow)
		#destinationText = "end"
		#if destination:
		#	destinationText = destination.text()
		#print(sourceText,destinationText)
		#match_user_file = re.search('fito_'+'.*'+'_(....-..-..)_([0-9]+).json',userfile)
		
	def workoutListRowChanged(self,row):
		print(self.workoutList.item(row).text(),"graph selected")	
#		selected_text = self.graphList.item(row).text()
#		
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

	def exercisesDoubleClicked(self, item):
		print("double clicked",item.text())
		
		
		if item.text() == "--insert superset--\n":
			self.superset_count += 1
			supersetHeader = QListWidgetItem("SUPERSET "+str(self.superset_count)+" HEADER")
			supersetHeader.setTextAlignment(Qt.AlignHCenter)
			supersetHeader.setBackground(self.palette().color(QPalette.ToolTipBase))
			self.setgroupList.addItem(supersetHeader)
			supersetFooter = QListWidgetItem("SUPERSET "+str(self.superset_count)+" FOOTER")
			supersetFooter.setTextAlignment(Qt.AlignHCenter)
			supersetFooter.setBackground(self.palette().color(QPalette.ToolTipBase))
			self.setgroupList.addItem(supersetFooter)
		else:
			self.setgroupList.addItem(item.text().splitlines()[0]+"\n")
	
	def exercisesListRowChanged(self,row):
		print("exercisesList",row)
#		if row != -1:
#			print(self.optionList.item(row).text())	
		


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
	
	
	

	window = Workout("red")
	window.do_update()
	#window.setFixedSize(800,600)
	window.resize(1200,800)
	window.show()

	app.exec_()
