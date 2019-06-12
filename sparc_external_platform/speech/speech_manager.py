import sys
sys.path.append('../')

import config as cfg
import json
import rospy
import speech.speech_config as speech_cfg
import threading

from std_msgs.msg import String


class SpeechManager:
	def __init__(self, app):
		self.fade_duration = speech_cfg.fade_duration
		self.robot_stream = cfg.robot_stream

		self.leds_service = None
		self.speech_service = None

		self.on_going_say_promise = None
		self.on_going_say_promise_canceled = False
		self.on_success = None
		self.on_fail = None
		self.timer = None
		self.listening = True
		self.save_listen_result_method = None
		self.listening_keywords = []

		if self.robot_stream and app:
			self.leds_service = app.session.service("ALLeds")
			self.speech_service = app.session.service("ALTextToSpeech")

		self.recognition_subscriber = rospy.Subscriber('/commands_text', String, self.on_text_received)

	def on_text_received(self, received_data):
		data = json.loads(received_data.data)
		if not data['text']:
			return

		if self.listening:
			self.check_speech_recognized(data['text'].strip().lower())

	def clear_say_attrs(self):
		self.on_going_say_promise = None
		self.on_success = None
		self.on_fail = None
		self.on_going_say_promise_canceled = False

	def say_async_callback(self, data):
		if not self.on_going_say_promise_canceled:
			if not data or data.hasError():
				if self.on_fail:
					self.on_fail()
			else:
				if self.on_success:
					self.on_success()
		self.clear_say_attrs()

	def say_async(self, text, on_success=None, on_fail=None):
		if self.robot_stream:
			self.on_success = on_success
			self.on_fail = on_fail
			if text:
				self.on_going_say_promise = self.speech_service.say(str(text), "English", _async=True)
				self.on_going_say_promise.addCallback(self.say_async_callback)
			else:
				on_fail()
		else:
			self.timer = threading.Timer(3, self.on_timeout, [on_success])
			self.timer.start()

	def stop_async(self):
		if self.robot_stream:
			if self.on_going_say_promise:
				self.on_going_say_promise_canceled = True
				if self.speech_service:
					self.speech_service.stopAll()
		else:
			if self.timer:
				self.timer.cancel()
			self.timer = None

	def on_timeout(self, on_timeout):
		self.timer = None
		self.clear_listen_attrs()
		if on_timeout:
			on_timeout()

	def listen(self, keywords, save_result=None, on_success=None, on_fail=None):
		if self.leds_service:
			self.leds_service.fadeRGB("FaceLeds", "blue", 0.5)
		self.listening_keywords = keywords
		self.save_listen_result_method = save_result
		self.on_success = on_success
		self.listening = True
		self.timer = threading.Timer(speech_cfg.time_to_listen, self.on_timeout, [on_fail])
		self.timer.start()

	def check_speech_recognized(self, text):
		if not self.listening_keywords and text:
			on_success = self.on_success
			self.clear_listen_attrs()
			if self.save_listen_result_method:
				self.save_listen_result_method(text)
			if on_success:
				on_success()
			return

		tokens = text.split(" ")
		for key in self.listening_keywords:
			if key in tokens:
				on_success = self.on_success
				self.clear_listen_attrs()
				if on_success:
					on_success(key)

	def stop_listen(self):
		self.clear_listen_attrs()

	def clear_listen_attrs(self):
		if self.leds_service:
			self.leds_service.fadeRGB("FaceLeds", "white", 0.5)
		if self.timer:
			self.timer.cancel()
		self.timer = None
		self.on_success = None
		self.on_fail = None
		self.listening = False
		self.listening_keywords = []


if __name__ == '__main__':
	speech_subscriber = SpeechManager(None)
