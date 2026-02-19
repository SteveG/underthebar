#!/usr/bin/env python3
""" Under The Bar

This is the main window of the "Under the Bar" application

It is just a window with a stacked layout and some buttons to navigate the stacked layout
"""

import sys, os, json
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,

    QHBoxLayout,
    QVBoxLayout,
    QStackedLayout,
    QWidget,
)
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtSvgWidgets
from PySide6.QtGui import QPalette, QColor, QIcon, QPixmap, QPainter
from utb_page_profile import Profile
#from utb_page_workout import Workout # This is a work in progress
from utb_page_analysis import Analysis
from utb_page_setting import Setting
from utb_page_routines import Routines
from utb_page_social import Social
import hevy_api


class UnderTheBar(QMainWindow):
	def __init__(self, sillytheme):
		super(UnderTheBar, self).__init__()
		script_folder = os.path.split(os.path.abspath(__file__))[0]
		
		
		self.setWindowTitle("UNDER THE BAR")
		self.setWindowIcon(self.loadIcon(script_folder+"/icons/dumbbell-solid.svg"))
		
		
		
		pagelayout = QVBoxLayout()
		toplayout = QHBoxLayout()
		contentlayout = QHBoxLayout()
		button_layout = QVBoxLayout()
		self.stacklayout = QStackedLayout()
		
		pagelayout.addLayout(toplayout)
		#toplayout.addWidget(Color("black"))

		toplayout.addStretch()
		toplayout.addWidget(QLabel('''<p align=center><u><font size="60">═|██══</font><font size="20">UNDER THE BAR</font><font size="60">══██|═</font></u><br><font size="2">powered by Hevy</font></p>'''))
		toplayout.addStretch()
		pagelayout.addLayout(contentlayout)
		contentlayout.addLayout(button_layout)
		contentlayout.addLayout(self.stacklayout)
		
		# dumb remove title bar
		if sillytheme:
			self.setWindowFlag(Qt.FramelessWindowHint, True)
			self.statusBar()
			qbtn = QPushButton("X")
			qbtn.setFlat(False)
			qbtn.setFixedSize(20,20)
			qbtn.clicked.connect(self.close)
			toplayout.addWidget(qbtn, alignment=Qt.AlignTop)
			toplayout.insertSpacing(0,20)
		
		
		#btn = QPushButton("🧍")
		btn = QPushButton()
		#btn.setStyleSheet("font-size: 40px;");
		btn.setIcon(self.loadIcon(script_folder+"/icons/user-solid.svg"))
		btn.setIconSize(QSize(48,48))
		btn.setCheckable(True)
		btn.setChecked(True)
		btn.setFlat(True)
		btn.setAutoExclusive(True);
		btn.pressed.connect(self.activate_profile)
		button_layout.addWidget(btn)
		self.stacklayout.addWidget(Profile("red"))

		btn = QPushButton()#("🏋️+")
		#btn.setStyleSheet("font-size: 40px;");
		btn.setIcon(self.loadIcon(script_folder+"/icons/dumbbell-solid.svg"))
		btn.setIconSize(QSize(48,48))
		btn.setCheckable(True)
		btn.setFlat(True)
		btn.setAutoExclusive(True);
		btn.pressed.connect(self.activate_workout)
		button_layout.addWidget(btn)
		self.stacklayout.addWidget(Routines("green"))

		btn = QPushButton()#("📈")
		#btn.setStyleSheet("font-size: 40px;");
		btn.setIcon(self.loadIcon(script_folder+"/icons/chart-line-solid.svg"))
		btn.setIconSize(QSize(48,48))
		btn.setCheckable(True)
		btn.setFlat(True)
		btn.setAutoExclusive(True);
		btn.pressed.connect(self.activate_analysis)
		button_layout.addWidget(btn)
		self.stacklayout.addWidget(Analysis("yellow"))


		btn = QPushButton()#("📈")
		#btn.setStyleSheet("font-size: 40px;");
		btn.setIcon(self.loadIcon(script_folder+"/icons/user-group-solid-full.svg"))
		btn.setIconSize(QSize(48,48))
		btn.setCheckable(True)
		btn.setFlat(True)
		btn.setAutoExclusive(True);
		btn.pressed.connect(self.activate_social)
		button_layout.addWidget(btn)
		self.stacklayout.addWidget(Social("brown"))
		
		button_layout.addStretch()
		
		btn = QPushButton()#("⚙️")
		#btn.setStyleSheet("font-size: 40px;");
		btn.setIcon(self.loadIcon(script_folder+"/icons/gear-solid.svg"))
		btn.setIconSize(QSize(48,48))
		btn.setCheckable(True)
		btn.setFlat(True)
		btn.setAutoExclusive(True);
		btn.pressed.connect(self.activate_settings)
		button_layout.addWidget(btn)
		self.stacklayout.addWidget(Setting("orange"))


		# profile default display so update it
		self.stacklayout.widget(0).do_update()
		
		widget = QWidget()
		widget.setLayout(pagelayout)
		self.setCentralWidget(widget)

	def loadIcon(self, path):
		img = QPixmap(path)
		qp = QPainter(img)
		qp.setCompositionMode(QPainter.CompositionMode_SourceIn)
		# You can enter any color you want here.
		qp.fillRect( img.rect(), QColor(self.palette().color(QPalette.Text)) ) 
		qp.end()
		ic = QIcon(img)
		return ic

	def activate_profile(self):
		self.stacklayout.widget(0).do_update()
		self.stacklayout.setCurrentIndex(0)


	def activate_workout(self):
		self.stacklayout.widget(1).do_update()
		self.stacklayout.setCurrentIndex(1)

	def activate_analysis(self):
		self.stacklayout.widget(2).do_update()
		self.stacklayout.setCurrentIndex(2)

	def activate_social(self):
		if not self.stacklayout.widget(3).initialised:
			self.stacklayout.widget(3).do_update()
		self.stacklayout.setCurrentIndex(3)

	def activate_settings(self):
		self.stacklayout.setCurrentIndex(4)
		
		

	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.offset = event.pos()
		else:
			super().mousePressEvent(event)

	def mouseMoveEvent(self, event):
		if hasattr(self, 'offset'):
			if self.offset is not None and event.buttons() == Qt.LeftButton:
				self.move(self.pos() + event.pos() - self.offset)
			else:
				super().mouseMoveEvent(event)

	def mouseReleaseEvent(self, event):
		self.offset = None
		super().mouseReleaseEvent(event)	
		
	def mouseDoubleClickEvent(self, event):
		state = self.windowState()
		if state == Qt.WindowMaximized:
			self.setWindowState(Qt.WindowNoState)
		elif state == Qt.WindowNoState:
			self.setWindowState(Qt.WindowMaximized)

		
class Color(QWidget):

	def __init__(self, color):
		super(Color, self).__init__()
		self.setAutoFillBackground(True)

		palette = self.palette()
		palette.setColor(QPalette.Window, QColor(color))
		self.setPalette(palette)
		
		self.setMinimumSize(50,50)


#import os
# from mainwindow import Ui_MainWindow

class Login(QtWidgets.QDialog):
	"""Login is a small dialog window that provides a means to log in to Hevy"""

	def __init__(self, parent=None):
		super(Login, self).__init__(parent)
		self.script_folder = os.path.split(os.path.abspath(__file__))[0]
			
			
		self.setWindowTitle("UNDER THE BAR")
		self.setWindowIcon(self.loadIcon(self.script_folder+"/icons/dumbbell-solid.svg"))

		self.logo = QtSvgWidgets.QSvgWidget(self.script_folder+"/icons/hevy-logo.svg")
		self.textName = QtWidgets.QLineEdit(self)
		self.textName.setPlaceholderText("Username")
		self.textName.setAlignment(QtCore.Qt.AlignCenter)
		self.textPass = QtWidgets.QLineEdit(self)
		self.textPass.setPlaceholderText("Password")
		self.textPass.setEchoMode(QtWidgets.QLineEdit.Password)
		self.textPass.setAlignment(QtCore.Qt.AlignCenter)
		self.buttonLogin = QtWidgets.QPushButton('Login', self)
		self.buttonLogin.clicked.connect(self.handleLogin)
		self.buttonAutoLogin = QtWidgets.QPushButton('Auto Firefox Cookie Login', self)
		self.buttonAutoLogin.clicked.connect(self.handleAutoLogin)
		
		layout = QtWidgets.QVBoxLayout(self)
		layout.addWidget(QtWidgets.QLabel('''<p align=center><u><font size="60">═|██══</font><font size="20">UNDER THE BAR</font><font size="60">══██|═</font></u><br><font size="2">powered by Hevy</font></p>'''))
		layout.addWidget(QtWidgets.QLabel('''<p align=center>To use Under The Bar you first need to log in to Hevy.</p> <p align=center>Enter your username and password below.</p><p> </p><p> </p>'''))
		layout.addWidget(self.logo)
		layout.addWidget(QtWidgets.QLabel('''<p align=center>Temporary work-around. Obtain values from Hevy web app login cookie.</p>'''))
		layout.addWidget(QtWidgets.QLabel('''<p align=center>Obtain by logging in to web app and using browser dev tools. </p>'''))
		layout.addWidget(QtWidgets.QLabel('''<p align=center>Can find in Hevy cookie "auth2.0-token"</p> '''))
		layout.addWidget(QtWidgets.QLabel('''<p align=center>Replace username with value for "access_token", password with value of "refresh_token"</p> <p> </p><p> </p>'''))
		layout.addWidget(self.textName)
		layout.addWidget(self.textPass)
		layout.addWidget(self.buttonLogin)
		
		layout.addWidget(QtWidgets.QLabel('''<p> </p><p> </p><p align=center>Or try our auto Firefox cookie find and login. Close Firefox first.</p> '''))
		layout.addWidget(self.buttonAutoLogin)

	def handleLogin(self):
		username = self.textName.text()
		password = self.textPass.text()
		self.buttonLogin.setIcon(self.loadIcon(self.script_folder+"/icons/spinner-solid.svg"))
		self.buttonLogin.repaint()
		#logged_in = hevy_api.login(username,password) # Work around necessary for Hevy API authorisation changes
		logged_in = hevy_api.temp_login(username,password)
		if logged_in ==200:
			self.accept()
		else:
			QtWidgets.QMessageBox.warning(
				self, 'Error', 'Bad user or password')
		self.buttonLogin.setIcon(QIcon())
		
	def handleAutoLogin(self):
		self.buttonAutoLogin.setIcon(self.loadIcon(self.script_folder+"/icons/spinner-solid.svg"))
		self.buttonAutoLogin.repaint()
		logged_in = hevy_api.cookie_login()
		if logged_in:
			self.accept()
		else:
			QtWidgets.QMessageBox.warning(
				self, 'Error', 'Bad user or password')
		self.buttonAutoLogin.setIcon(QIcon())
		
	def loadIcon(self, path):
		img = QtGui.QPixmap(path)
		qp = QtGui.QPainter(img)
		qp.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
		# You can enter any color you want here.
		qp.fillRect( img.rect(), QtGui.QColor(self.palette().color(QPalette.Text)) ) 
		qp.end()
		ic = QtGui.QIcon(img)
		return ic
		
		
if __name__ == "__main__":
	#windows sillyness
	import ctypes, platform
	if platform.system() == "Windows":
		myappid = u'underthebar.awesome'
		ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
	
	app = QApplication(sys.argv)
	
	sillytheme = True
	
	if sillytheme:
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
	
	home_folder = str(Path.home())
	utb_folder = home_folder + "/.underthebar"

	# Check whether user is logged in, if not do the login window
	session_data = {}
	if not os.path.exists(utb_folder+"/session.json"):	
		login = Login()
		if login.exec_() != QtWidgets.QDialog.Accepted:
			sys.exit()
	else:
		with open(utb_folder+"/session.json", 'r') as file:
			session_data = json.load(file)
			# if "auth-token" not in session_data: #Hevy API update
			if "access_token" not in session_data:
				login = Login()
				if login.exec_() != QtWidgets.QDialog.Accepted:
					sys.exit()


	window = UnderTheBar(sillytheme)
	#window.setFixedSize(800,600)
	window.resize(1280,900)
	window.show()

	#hevy_api.hello()

	app.exec_()
