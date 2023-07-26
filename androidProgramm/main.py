from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.properties import StringProperty
from kivy.graphics.vertex_instructions import Rectangle, Ellipse, Line
from kivy.graphics.context_instructions import Color
from kivy.uix.label import Label
from kivy.uix.button import Button

import random
import threading
import requests
import time


URL_TO_PARSE = 'https://getmytemperature.pythonanywhere.com/json'
TIMEOUT = 5

MN = 1
WINDOW_SIZE = Window.size
degreesMax = 200



class MainField(Widget):
	data = []
	WORKING = False
	nowTemperature = 0

	def gettingData(self):
		while self.WORKING:
			try: 
				gettedData = requests.get(URL_TO_PARSE, timeout=TIMEOUT).text
				self.data = list(map(float, gettedData.split('<br>')[:-1]))
			except Exception as error: print(error); self.data = []
			
			self.nowTemperature = self.data[-1] if len(self.data) > 0 else 0
			time.sleep(1)


	def drawScreen(self, *args):
		self.nowTemperature = self.data[-1] if len(self.data) > 0 else 0

		martixOfGraphic = []
		countOfDatas = len(self.data)

		for num in range(0, countOfDatas):
			gettedData = self.data[num] + 100
			if gettedData > degreesMax: gettedData = degreesMax

			martixOfGraphic.append((
				round(WINDOW_SIZE[0] / countOfDatas * num), # X
				round(WINDOW_SIZE[1] / 3 * 2 / degreesMax * gettedData) # Y
			))

		self.canvas.before.clear()
		self.canvas.after.clear()

		with self.canvas.before:
			Color(1, 1, 1, 0.07)
			Rectangle(
				pos=(0, 0),
				size=(WINDOW_SIZE[0], round(WINDOW_SIZE[1] / 3 * 2)) 
			)
			Line(
				size=(3, WINDOW_SIZE[0]),
				pos=(0, round(round(WINDOW_SIZE[1] / 3 * 2) / 2) ),
				color=(1, 1, 1, 1)
			)

		with self.canvas.after:
			for position in martixOfGraphic:
				if martixOfGraphic[martixOfGraphic.index(position) - 1][1] < position[1] and martixOfGraphic.index(position) >= 0:
					Color(0, 1, 0, 1)
				else:
					Color(1, 0, 0, 1)

				Rectangle(pos=position, size=(5, 5))



class MainApp(App):
	WORKING = True
	parentWidget = BoxLayout(orientation='vertical')


	def __init__(self, **kwargs):
		super(MainApp, self).__init__(**kwargs)
		Window.bind(on_request_close=self.close)

	def drawFullScreen(self):
		if self.parentWidget:
			self.parentWidget.add_widget(
				Button(
					text=f"{str(self.mainField.nowTemperature)} °C",
					font_size=80,
					size_hint=(1, 0.4),
					halign='center',
					pos_hint={"top": 1},
					padding=(10, 10),
					on_press=self.on_touch,
					background_color=(0, 0, 0, 1)
				)
			)

			self.parentWidget.add_widget(self.mainField)

	def build(self):
		self.mainField = MainField()
		self.mainField.WORKING = True
		self.mainField.drawScreen()
		threading.Thread(target=self.mainField.gettingData).start()
		self.drawFullScreen()

		return self.parentWidget

	def close(self, touch):
		self.mainField.WORKING = False
		self.WORKING = False

	def on_touch(self, *args):
		if self.parentWidget:
			for widg in self.parentWidget.children[::-1]:
				self.parentWidget.remove_widget(widg)

			self.drawFullScreen()
			self.mainField.drawScreen()		


if __name__ == '__main__': MainApp().run()