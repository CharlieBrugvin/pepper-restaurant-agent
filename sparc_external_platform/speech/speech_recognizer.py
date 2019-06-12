import sys
sys.path.append('../')

import config as cfg
import json
import rospy
import speech_recognition as sr
import traceback
import unidecode
import time # update charlie

from std_msgs.msg import String
from speech.pepper_microphone import PepperSpeechRecognitionEngine



class SpeechRecognizer:
	def __init__(self, audio_stream=cfg.audio_stream):
		self.audio_stream = audio_stream
		self.publisher = rospy.Publisher('commands_text', String, queue_size=10)

		if self.audio_stream:
			if not cfg.robot_stream:
				self.microphone = sr.Microphone()
				self.engine = sr.Recognizer()
			else:
				self.pepper_engine = PepperSpeechRecognitionEngine(False)

		self.rate = rospy.Rate(10)

		print('Used language for recognition: ' + cfg.language)

	def recognize_speech(self):
		response = {
			'text': None,
			'error': None,
			'time_stop_speaking': None, # update charlie
			'language': cfg.language
		}
		if self.audio_stream:
			if cfg.robot_stream:
				print("Listening")
				audio = self.pepper_engine.listen()
				print("Recognizing")

				time_stop_speaking = time.time() - 1 # update charlie : we calcualate the speech end date 

				response['text'] = self.pepper_engine.recognize_google(audio, cfg.language, False)
				if response['text']:
					response['text'] = unidecode.unidecode(response['text'])
					response['time_stop_speaking'] = time_stop_speaking # we publish it
			else:
				with self.microphone as source:
					self.engine.adjust_for_ambient_noise(source)
					audio = self.engine.listen(source)
				try:
					response['text'] = self.engine.recognize_google(audio, language=cfg.language)
					if response['text']:
						response['text'] = unidecode.unidecode(response['text'])
				except sr.RequestError:
					response['error'] = 'API unavailable'
				except sr.UnknownValueError:
					response['error'] = 'Unable to recognize speech'
		else:
			response['text'] = raw_input("Query: ")

		if response['text'] and response['text'].lower() == 'exit':
			exit(0)

		return response

	def run(self):
		try:
			while not rospy.is_shutdown():
				speech = self.recognize_speech()
				print("Recognized speech:\n\t%s" % speech)
				if speech and speech['text']:
					self.publisher.publish(json.dumps(speech))
					self.rate.sleep()

		except KeyboardInterrupt:
			print('Forced interruption by user, shutting down...')

		except Exception as e:
			print('Thrown exception: ' + str(e))
			traceback.print_exc()

		except rospy.ROSInterruptException:
			print('ROS error')


if __name__ == '__main__':
	user_response = raw_input("Audio stream? [y/n]: ")
	if user_response == 'no' or user_response == 'n':
		use_audio_stream = False

	speech_recognizer = SpeechRecognizer(use_audio_stream)
	speech_recognizer.run()