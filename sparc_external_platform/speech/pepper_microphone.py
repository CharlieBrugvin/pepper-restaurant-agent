import rospy
import pyaudio
import struct
from urllib import urlencode, urlopen
import json
from urllib2 import Request, urlopen
from naoqi_bridge_msgs.msg import AudioBuffer
from speech_recognition import AudioData
import audioop
from collections import deque


class PepperSpeechRecognitionEngine:
	def __init__(self, play_back=True):
		rospy.init_node('mic_listener', anonymous=True)

		self.microphone_buffer = deque(maxlen=10000)
		self.play_back = play_back
		self.CHUNK = 1024
		self.SAMPLE_WIDTH = 4
		self.PY_AUDIO_FORMAT = pyaudio.paInt16
		self.SAMPLE_RATE = 48000
		self.CHANNELS_NO = 4

		self.max_frames_after_stop = 10
		self.frames_after_stop = 0
		self.first_speech_frame = None

		self.key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
		self.talking = False

		self.min_energy_threshold = 80000000

		self.energy_threshold = 70000000  # minimum audio energy to consider for recording
		self.dynamic_energy_threshold = True
		self.dynamic_energy_adjustment_damping = 0.15
		self.dynamic_energy_ratio = 1.5
		self.pause_threshold = 0.8
		self.operation_timeout = None

		self.phrase_threshold = 0.3
		self.non_speaking_duration = 0.5

		if play_back:
			self.output_stream = pyaudio.PyAudio().open(format=self.PY_AUDIO_FORMAT,
													 channels=self.CHANNELS_NO,
													 rate=self.SAMPLE_RATE,
													 output=True,
													 frames_per_buffer=self.CHUNK)

		self.stream = None

		self.audio_subscriber = rospy.Subscriber('/pepper_robot/naoqi_driver/audio', AudioBuffer, self.on_audio_received)

	def adjust_for_ambient_noise(self):
		return

	def listen(self):
		while not self.talking:
			pass

		while self.talking:
			pass

		speech_data = []
		list_buffer = list(self.microphone_buffer)
		for i in list_buffer[list_buffer.index(self.first_speech_frame) - 10:]:
			speech_data += list(i)

		output = struct.pack('<' + ('h' * len(speech_data)), *speech_data)
		if self.play_back:
			self.output_stream.write(output)
		self.first_speech_frame = None

		audio_data_new = AudioData(output, 96000, 4)

		return audio_data_new

	def on_audio_received(self, data):
		self.microphone_buffer.append(data.data)
		output = struct.pack('<' + ('h' * len(data.data)), *data.data)

		seconds_per_buffer = 0.33

		energy = audioop.rms(output, self.SAMPLE_WIDTH)
		if energy > self.energy_threshold:
			if not self.talking:
				print("Started talking")
				self.first_speech_frame = data.data
				self.frames_after_stop = 0

			self.talking = True
		else:
			if self.frames_after_stop >= self.max_frames_after_stop:
				if self.talking:
					print("Stopped talking")
				self.talking = False

			self.frames_after_stop = min(self.max_frames_after_stop, self.frames_after_stop + 1)

		if self.dynamic_energy_threshold:
			damping = self.dynamic_energy_adjustment_damping ** seconds_per_buffer
			target_energy = energy * self.dynamic_energy_ratio
			self.energy_threshold = min(self.min_energy_threshold, self.energy_threshold * damping + target_energy * (1 - damping))

		if self.play_back:
			self.output_stream.write(output)

	def recognize_google(self, audio_data, language, show_all=False):
		print("Sending frame data")
		flac_data = audio_data.get_flac_data(convert_width=2, convert_rate=self.SAMPLE_RATE)

		# update charlie
		import time
		f = open("pepper_audio_files/"+ str(time.time()) +".flac", "w")
		f.write(flac_data)
		# end update
		
		url = "http://www.google.com/speech-api/v2/recognize?{}".format(urlencode({
			"client": "chromium",
			"lang": language,
			"key": self.key,
		}))

		request = Request(url, data=flac_data, headers={"Content-Type": "audio/x-flac; rate={}".format(self.SAMPLE_RATE)})
		response = urlopen(request)
		response_text = response.read().decode("utf-8")
		actual_result = []
		for line in response_text.split("\n"):
			if not line: continue
			result = json.loads(line)["result"]
			if len(result) != 0:
				actual_result = result[0]
				break

		# return results
		if show_all: return actual_result

		if not isinstance(actual_result, dict) or len(
			actual_result.get("alternative", [])) == 0: return {}
		if "confidence" in actual_result["alternative"]:
			# return alternative with highest confidence score
			best_hypothesis = max(actual_result["alternative"], key=lambda alternative: alternative["confidence"])
		else:
			# when there is no confidence available, we arbitrarily choose the first hypothesis.
			best_hypothesis = actual_result["alternative"][0]
		if "transcript" not in best_hypothesis: return {}
		return best_hypothesis["transcript"]
