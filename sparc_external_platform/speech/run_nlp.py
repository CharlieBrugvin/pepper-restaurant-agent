import sys
sys.path.append('../')

import rospy

from natural_language_processor import NaturalLanguageProcessor
from speech_recognizer import SpeechRecognizer
from std_msgs.msg import String


class NLP:
	def __init__(self, audio_stream):
		self.speech_recognizer = SpeechRecognizer(audio_stream)
		self.natural_language_processor = NaturalLanguageProcessor()

	def run(self):
		self.speech_recognizer.run()


if __name__ == '__main__':
	def print_data(data):
		pass

	rospy.init_node('mic_listener', anonymous=True)
	rospy.Subscriber('/commands_structured', String, print_data)

	use_audio_stream = True
	user_response = raw_input("Audio stream? [y/n]: ")
	if user_response == 'no' or user_response == 'n':
		use_audio_stream = False

	nlp = NLP(use_audio_stream)
	nlp.run()
