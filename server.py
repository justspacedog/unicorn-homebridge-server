#!/usr/bin/env python

import json

import os
import threading
import math
import colorsys
from time import sleep
from datetime import datetime
from gpiozero import CPUTemperature
from lib.unicorn_wrapper import UnicornWrapper
from flask import Flask, jsonify, make_response, request, send_from_directory
from flask_cors import CORS
from random import randint
from jsmin import jsmin

blinkThread = None
crntColors = None
globalRed = 0
globalGreen = 0
globalBlue = 0
globalColour = 0
globalBrightness = 0
globalLastCalled = None
globalLastCalledApi = None
globalStatus = None
globalStatusOverwrite = False
globalFistRun = False

# Initialize the Unicorn hat
unicorn = UnicornWrapper()

# get the width and height of the hardware and set it to portrait if its not
width, height = unicorn.getShape()


class MyFlaskApp(Flask):
	def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
		if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
			with self.app_context():
				startupRainbow()
		super(MyFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = MyFlaskApp(__name__, static_folder='frontend/build', static_url_path='')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


def setColor(r, g, b, brightness=0.5, speed=None):
	global globalFirstRun, globalBrightness, crntColors

	if globalBrightness is 0:
		globalBrightness = 1.0

	setPixels(r, g, b, brightness)
	unicorn.show()
	switchOn()

	if speed is not None and speed != '':
		crntT = threading.currentThread()
		unicorn.clear()
		while getattr(crntT, "do_run", True):
			setPixels(r, g, b, brightness)
			unicorn.show()
			sleep(speed)
			unicorn.clear()
			unicorn.show()
			sleep(speed)


def setPixels(r, g, b, brightness):
	global globalRed, globalGreen, globalBlue, globalBrightness

	globalRed = r
	globalGreen = g
	globalBlue = b

#	if brightness is 0:
#		brightness = 0.5

	globalBrightness = brightness

	unicorn.setBrightness(globalBrightness)
	unicorn.setColour(r, g, b)

def switchOn():
	global blinkThread, globalFirstRun, globalBlue, globalGreen, globalRed, globalBrightness, globalStatus

	if globalFirstRun is True:
		if globalBrightness is 0:
			globalBrightness = 1.0
		globalFirstRun = False

	setPixels(globalRed, globalGreen, globalBlue, globalBrightness)

	globalStatus = 'on'
#	rgb = unicorn.hsvIntToRGB(globalBlue, globalGreen, globalRed)
#	blinkThread = threading.Thread(target=setColor, args=(rgb[0], rgb[1], rgb[2]))
#	blinkThread.do_run = True
#	blinkThread.start()

def switchOff():
	global blinkThread, globalRed, globalGreen, globalBlue, globalStatus
#	globalRed = 0
#	globalGreen = 0
#	globalBlue = 0
	if blinkThread is not None:
		blinkThread.do_run = False
	unicorn.clear()
	unicorn.off()
	globalStatus = 'off'

def halfBlink():
	unicorn.show()
	sleep(0.8)
	unicorn.clear()
	unicorn.show()
	sleep(0.2)


def countDown(time):
	showTime = time - 12
	brightness = 0.5
	while showTime > 0:
		b = brightness
		for x in range(4):
			b = b - x
			setPixels(255, 255, 0, b)
			unicorn.show()
			sleep(0.5)
			unicorn.clear()
		unicorn.show()
		sleep(2)
		showTime = showTime - 2
	for i in range(10):
		setPixels(255, 0, 0, 0.5)
		halfBlink()
	setColor(255, 0, 0, 0.5)
	halfBlink()
	unicorn.clear()
	unicorn.off()


def displayRainbow(brightness, speed, run=None):
	global globalFirstRun, crntColors
	if speed is None:
		speed = 0.1
#	if brightness is None:
#		brightness = 0.5
	crntT = threading.currentThread()
	i = 0.0
	offset = 30
	while getattr(crntT, "do_run", True):
		i = i + 0.3
		if globalFirstRun is False:
			unicorn.setBrightness(brightness)
		for x in range(0, width):
			for y in range(0, height):
				r = 0  # x * 32
				g = 0  # y * 32
				xy = x + y / 4
				r = (math.cos((x + i) / 2.0) + math.cos((y + i) / 2.0)) * 64.0 + 128.0
				g = (math.sin((x + i) / 1.5) + math.sin((y + i) / 2.0)) * 64.0 + 128.0
				b = (math.sin((x + i) / 2.0) + math.cos((y + i) / 1.5)) * 64.0 + 128.0
				r = max(0, min(255, r + offset))
				g = max(0, min(255, g + offset))
				b = max(0, min(255, b + offset))
				unicorn.setPixel(x, y, int(r), int(g), int(b))

		unicorn.show()
		sleep(speed)


def setTimestamp():
	global globalLastCalled
	globalLastCalled = datetime.now()


# API Initialization
@app.route('/', methods=['GET'])
def root():
	print(app.static_folder)
	return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/on', methods=['GET', 'POST'])
def apiOn():
	global globalStatusOverwrite, globalStatus, globalLastCalledApi
	globalStatusOverwrite = False
	globalStatus = 'on'
	globalLastCalledApi = '/api/on'
	switchOff()
	switchOn()
	setTimestamp()
	unicorn.show()
	return make_response(jsonify({}))


@app.route('/api/off', methods=['GET', 'POST'])
def apiOff():
	global crntColors, globalStatusOverwrite, globalStatus, globalLastCalledApi
	globalStatusOverwrite = False
	globalStatus = 'off'
	globalLastCalledApi = '/api/off'
	crntColors = None
	switchOff()
	setTimestamp()
	return make_response(jsonify({}))


@app.route('/api/switch', methods=['POST'])
def apiSwitch():
	global blinkThread, globalStatusOverwrite, globalStatus, globalLastCalledApi

	if globalStatusOverwrite:
		return make_response(jsonify({}))

	globalLastCalledApi = '/api/switch'
	switchOff()
	content = json.loads(jsmin(request.get_data(as_text=True)))
	red = content.get('red', None)
	green = content.get('green', None)
	blue = content.get('blue', None)
	if red is None or green is None or blue is None:
		return make_response(jsonify({'error': 'red, green and blue must be present and can\' be empty'}), 500)

	if red == 0 and green == 144 and blue == 0:
		globalStatus = 'Available'
	elif red == 255 and green == 191 and blue == 0:
		globalStatus = 'Away'
	elif red == 179 and green == 0 and blue == 0:
		globalStatus = 'Busy'
	else:
		globalStatus = None

	brightness = content.get('brightness', None)
	speed = content.get('speed', None)
	blinkThread = threading.Thread(target=setColor, args=(red, green, blue, brightness, speed))
	blinkThread.do_run = True
	blinkThread.start()
	setTimestamp()
	return make_response(jsonify())

@app.route('/api/available', methods=['GET', 'POST'])
def availableCall():
	global globalStatusOverwrite, globalStatus, globalBrightness, globalLastCalledApi, blinkThread
	globalStatusOverwrite = True
	globalStatus = 'Available'
	globalLastCalledApi = '/api/available'
	switchOff()
	blinkThread = threading.Thread(target=setColor, args=(0, 144, 0))
	blinkThread.do_run = True
	blinkThread.start()
	setTimestamp()
	return make_response(jsonify())

@app.route('/api/busy', methods=['GET', 'POST'])
def busyCall():
	global globalStatusOverwrite, globalStatus, globalBrightness, globalLastCalledApi, blinkThread
	globalStatusOverwrite = True
	globalStatus = 'Busy'
	globalLastCalledApi = '/api/busy'
	switchOff()
	blinkThread = threading.Thread(target=setColor, args=(179, 0, 0))
	blinkThread.do_run = True
	blinkThread.start()
	setTimestamp()
	return make_response(jsonify())

@app.route('/api/away', methods=['GET', 'POST'])
def awayCall():
	global globalStatusOverwrite, globalStatus, globalBrightness, globalLastCalledApi, blinkThread
	globalStatusOverwrite = True
	globalStatus = 'Away'
	globalLastCalledApi = '/api/away'
	switchOff()
	blinkThread = threading.Thread(target=setColor, args=(255, 191, 0))
	blinkThread.do_run = True
	blinkThread.start()
	setTimestamp()
	return make_response(jsonify())

@app.route('/api/reset', methods=['GET', 'POST'])
def resetCall():
	global globalStatusOverwrite, globalStatus, globalLastCalledApi, blinkThread
	globalStatusOverwrite = False
	return make_response(jsonify())


@app.route('/api/rainbow', methods=['GET', 'POST'])
def apiDisplayRainbow():
	global blinkThread, globalStatus, globalLastCalledApi
	switchOff()
	globalStatus = 'rainbow'
	globalLastCalledApi = '/api/rainbow'
#	data = request.get_data(as_text=True)
#	content = json.loads(jsmin(request.get_data(as_text=True)))
#	brightness = content.get('brightness', None)
#	speed = content.get('speed', None)
#	blinkThread = threading.Thread(target=displayRainbow, args=(brightness, speed, None))
	blinkThread = threading.Thread(target=displayRainbow, args=(1.0, 0.1, None))
	blinkThread.do_run = True
	blinkThread.start()
	setTimestamp()
	return make_response(jsonify())

@app.route('/api/status', methods=['GET'])
def apiStatus():
	global globalStatusOverwrite, globalStatus, globalRed, globalGreen, globalBlue, globalBrightness, \
			globalLastCalled, globalLastCalledApi, width, height, unicorn

	cpu = CPUTemperature()
	return jsonify({
		'red': globalRed,
		'green': globalGreen,
		'blue': globalBlue,
		'brightness': globalBrightness,
		'lastCalled': globalLastCalled,
		'cpuTemp': cpu.temperature,
		'lastCalledApi': globalLastCalledApi,
		'height': height,
		'width': width,
		'unicorn': unicorn.getType(),
		'status': globalStatus,
		'statusOverwritten': globalStatusOverwrite
	})

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

def startupRainbow():
	global globalFirstRun, globalRed, globalGreen, globalBlue, globalBrightness, globalStatus, blinkThread
	if globalRed is 0:
		 globalRed = 215
	if globalGreen is 0:
		 globalGreen = 145
	if globalBlue is 0:
		 globalBlue = 75
	if globalBrightness is 0:
		 globalBrightness = 1.0
		 unicorn.setBrightness(globalBrightness)
	globalFirstRun = True

	globalStatus = 'rainbow'

	blinkThread = threading.Thread(target=displayRainbow, args=(1, 0.1, 1))
	blinkThread.do_run = True
	blinkThread.start()

# fadeout the startupRainbow while we are waiting for the homebridge.service to start
	threading.Thread(target=fadeout).start()

def fadeout():
	import time as t
	global globalFirstRun, globalBrightness

	seconds = 300-90 # my homebridge needs approximately 5 minutes to start, this server is started after 90 seconds
	brightness = 100+25 # under brightness of 0.25 there might not be a rainbow, so we start 25 steps above - if it is over 100, the first 25 setps are treated as 100
	if globalBrightness > 100:
		 globalBrightness = 1.0
	else:
		 globalBrightness = float(brightness/100)

	for s in range(seconds):
		if globalFirstRun is False:
			 globalBrightness = 1.0
			 return # stop if there was an brightness or color setting done by this server over HTTP
		if (brightness > seconds):
			 print("brightness value needs to be smaller or same than seconds value, otherwise round() will be zero and devision by zero is not possible")
			 return
		elif (globalBrightness < 0.25):
			 print("brightness is getting too small, turning off rainbow")
			 globalFirstRun = False
			 globalBrightness = 1.0
			 switchOff()
			 return
		elif ((s%round((seconds//(brightness-25)), 0) == 0)): # reduce brightness every time when the current second [s] can be devided with seconds/brightness -> fadeout steps are smooth
			if brightness-s > 100:
				globalBrightness = 1.0
			unicorn.setBrightness(globalBrightness)
			print(str(globalBrightness))
			globalBrightness -= 0.01
		t.sleep(1)

# Homebridge APIs
def rgb_to_hex(rgb):
	return '%02x%02x%02x' % rgb

@app.route('/api/hb-status/<string:st>', methods=['GET'])
def homebridgeStatus(st):
	global globalStatus

	if st == 'switch': # 0 or 1
		status = 1 # default (on startup) is 'on' -> 1

		if globalStatus is 'off' or globalStatus is 'rainbow':
			status = 0 # when it is turned off

		return str(status)

	elif st == 'color': # hex color
		global globalRed, globalGreen, globalBlue
		return str(rgb_to_hex((globalRed, globalGreen, globalBlue)))

	elif st == 'brightness': # 0 to 100
		global globalBrightness
		return str(globalBrightness*100)[:-2]

	elif st == 'rainbow':
		statusr = 0

	if globalStatus is 'rainbow':
		 statusr = 1

	return str(statusr)

@app.route('/api/set/<string:c>', methods=['GET'])
def set_colour(c):
	global globalStatus, globalRed, globalGreen, globalBlue

	switchOff()

	rgb = unicorn.htmlToRGB(c)
	globalRed = rgb[0]
	globalGreen = rgb[1]
	globalBlue = rgb[2]

	unicorn.setColour(globalRed, globalGreen, globalBlue)

	if globalStatus != 'on':
		switchOn()
		globalStatus = 'on'
	return jsonify({'status': globalStatus, 'colourR': globalRed, 'colourG': globalGreen, 'colourB': globalBlue})

@app.route('/api/setb/<string:b>', methods=['GET'])
def set_brightness(b):
	global globalStatus, globalBrightness

	switchOff()

	globalBrightness = float(int(b)/100)
	unicorn.setBrightness(globalBrightness)	

	if globalStatus != 'on':
		switchOn()
		globalStatus = 'on'
	return jsonify({'status': globalStatus, 'brightness': globalBrightness})

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False)
