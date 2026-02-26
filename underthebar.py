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
		self.textName.setPlaceholderText("Access Token")
		self.textName.setAlignment(QtCore.Qt.AlignCenter)
		self.textPass = QtWidgets.QLineEdit(self)
		self.textPass.setPlaceholderText("Refresh Token")
		self.textPass.setEchoMode(QtWidgets.QLineEdit.Password)
		self.textPass.setAlignment(QtCore.Qt.AlignCenter)
		self.buttonLogin = QtWidgets.QPushButton('Login', self)
		self.buttonLogin.clicked.connect(self.handleLogin)
		self.buttonAutoLogin = QtWidgets.QPushButton('Auto Firefox Cookie Login', self)
		self.buttonAutoLogin.clicked.connect(self.handleAutoLogin)
		
		layout = QtWidgets.QVBoxLayout(self)
		layout.addWidget(QtWidgets.QLabel('''<p align=center><u><font size="60">═|██══</font><font size="20">UNDER THE BAR</font><font size="60">══██|═</font></u><br><font size="2">powered by Hevy</font></p>'''))
		layout.addWidget(QtWidgets.QLabel('''<p align=center>To use Under The Bar you first need to log in to Hevy. But the web login didn't work ????</p> <p align=center>Enter your credentials below.</p><p> </p><p> </p>'''))
		layout.addWidget(self.logo)
		layout.addWidget(QtWidgets.QLabel('''<p align=center>Obtain the credential from the Hevy web app login cookie.</p>'''))
		layout.addWidget(QtWidgets.QLabel('''<p align=center>Can get this by logging in to web app and using browser dev tools. </p>'''))
		layout.addWidget(QtWidgets.QLabel('''<p align=center>Can find in Hevy cookie "auth2.0-token". Need to enter the values of "access_token" and "refresh_token" below.</p> '''))
		layout.addWidget(QtWidgets.QLabel('''<p align=center>If you are just offline but have logged in previously, just close this and the app should open but data sync won't work.</p> <p> </p><p> </p>'''))
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

# #
# # New log in method that opens up a web view to the hevy website and retrieves the login cookie when the user logs in
# # Very nice but makes the windows bundle very large as we're basically including a web browser with QWebEngine
# #
# # new stuff for web log in
# import sys
# from PySide6.QtWidgets import QApplication, QMainWindow
# from PySide6.QtWebEngineCore import QWebEngineProfile
# from PySide6.QtWebEngineWidgets import QWebEngineView
# from PySide6.QtCore import QUrl
# import urllib.parse
# import json

# class HevyLogin(QMainWindow):
	# def __init__(self):
		# super().__init__()
		# self.setWindowTitle("You Need to log in to Hevy")
		# self.resize(600, 800)

		# # 1. Setup WebView
		# self.browser = QWebEngineView()
		# self.setCentralWidget(self.browser)

		# # 2. Get the Cookie Store from the profile
		# self.profile = QWebEngineProfile.defaultProfile()
		# self.cookie_store = self.profile.cookieStore()

		# # 3. Connect the signal to our handler function
		# self.cookie_store.cookieAdded.connect(self.on_cookie_added)

		# # 4. Load a URL (e.g., httpbin.org which sets cookies)
		# self.browser.setUrl(QUrl("https://hevy.com/login"))

	# def on_cookie_added(self, cookie):
		# # This function is triggered whenever a new cookie is added
		# name = cookie.name().data().decode('utf-8')
		# value = cookie.value().data().decode('utf-8')
		# domain = cookie.domain()
		# print(f"New Cookie Added: {name} = {value} (Domain: {domain})")

		# if name == "auth2.0-token":
			# cookie_json = json.loads(urllib.parse.unquote(value))
			# print("access_token", cookie_json["access_token"])
			# print("expires_at", cookie_json["expires_at"])
			# print("refresh_token", cookie_json["refresh_token"])
			
			
			# # save the session data
			# home_folder = str(Path.home())
			# utb_folder = home_folder + "/.underthebar"
			# session_data = {}
			# if os.path.exists(utb_folder+"/session.json"):
				# with open(utb_folder+"/session.json", 'r') as file:
					# session_data = json.load(file)
			# # potentially not the same user logged in so remove user-id from session if exists
			# if "user-id" in session_data:
				# del session_data["user-id"]
			# session_data["access_token"] = cookie_json["access_token"]
			# session_data["expires_at"] = cookie_json["expires_at"]
			# session_data["refresh_token"] = cookie_json["refresh_token"]
			# with open(utb_folder+"/session.json", 'w') as f:
				# json.dump(session_data,f)
			# self.close()

#
# The lightweight version of web login, uses pywebview which uses native OS renderer so we don't need to bundle a whole browser ourselves
#
import webview
import urllib.parse
import json

# Just print what the native renderer is for info
def on_initialized(renderer):
    print(f'GUI is initialized with renderer: {renderer}')

def on_loaded(window):
    print('DOM is ready')

    # unsubscribe event listener, subscribe to web/api responses
    window.events.loaded -= on_loaded
    window.events.response_received += on_response
	
# Not entirely sure this will work on Mac
def on_response(window, response):
    #print('Response recevied:', response.url)
	if response.url == 'https://api.hevyapp.com/login':
		print("----login response----") 
		
		# Don't seem to be able to get the actual response data(?), check if a cookie got created instead
		cookies = window.get_cookies()
		for c in cookies:
			if("auth2.0-token" in c):
				try:
					cookie_json = json.loads(urllib.parse.unquote(c["auth2.0-token"].value))
					print(cookie_json)
					window.events.response_received -= on_response


					# save the session data
					home_folder = str(Path.home())
					utb_folder = home_folder + "/.underthebar"
					session_data = {}
					if os.path.exists(utb_folder+"/session.json"):
						with open(utb_folder+"/session.json", 'r') as file:
							session_data = json.load(file)
					# potentially not the same user logged in so remove user-id from session if exists
					if "user-id" in session_data:
						del session_data["user-id"]
					session_data["access_token"] = cookie_json["access_token"]
					session_data["expires_at"] = cookie_json["expires_at"]
					session_data["refresh_token"] = cookie_json["refresh_token"]
					with open(utb_folder+"/session.json", 'w') as f:
						json.dump(session_data,f)
					
					window.destroy()
					
				except:
					print("not valid")	
		
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
	
	
	# Best new way of logging in
	if not hevy_api.is_logged_in()[0]:
		window = webview.create_window(
			'You need to log in to Hevy', 'https://hevy.com/login', confirm_close=False, frameless=False, width=400, height=800
		)
		window.events.initialized += on_initialized
		window.events.loaded += on_loaded
		print("Starting webview")
		webview.start()
		print("Finished webview")
	
	# # new way of logging in, uses QTWebEngine and is way to heavy for distributing
	# if not hevy_api.is_logged_in()[0]:
		# window = HevyLogin()
		# window.show()
		# print("running Hevy login")
		# app.exec()
	# else:
		# print("already logged in to Hevy")
		
	home_folder = str(Path.home())
	utb_folder = home_folder + "/.underthebar"

	# Check whether user is logged in now, if not do the old login window
	session_data = {}
	#if not os.path.exists(utb_folder+"/session.json"):	
	if not hevy_api.is_logged_in()[0]:
		login = Login()
		if login.exec_() != QtWidgets.QDialog.Accepted:
			#sys.exit()
			with open(utb_folder+"/session.json", 'r') as file:
				session_data = json.load(file)
				# if "auth-token" not in session_data: #Hevy API update
			if "access_token" not in session_data: #We'll allow the app to open at least, user might just be offline
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
