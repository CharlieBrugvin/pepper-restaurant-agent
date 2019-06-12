import environment_config as cfg
import json
import rospy
import threading
import traceback

from std_msgs.msg import String


# {power: on/off,
#  color: red/white/orange/yellow/cyan/green/blue/purple/pink,
#  brightness: -1|1,
#  }


class LightsActuator:
	def __init__(self):
		self.running = False
		self.publishers = {}
		for target_id, topic in cfg.lights_topics.items():
			self.publishers[target_id] = rospy.Publisher(target_id, String, queue_size=10)

	def process_command(self, optional_entities=None, on_success=None, on_fail=None):
		self.running = True
		if not optional_entities:
			self.running = False
			if on_fail:
				on_fail()
			return
		try:
			if optional_entities and cfg.target_id in optional_entities:
				if optional_entities[cfg.target_id] in cfg.lights_topics:
					self.run_command(optional_entities[cfg.target_id], optional_entities)
			else:
				for topic_id in cfg.lights_topics.keys():
					self.run_command(topic_id, optional_entities)
			if on_success:
				on_success()
		except Exception as e:
			print("Thrown exception: " + str(optional_entities) + " " + str(e))
			traceback.print_exc()
			if on_fail:
				on_fail()
		self.running = False

	def run_command(self, target_id, optional_parameters):
		data = {}
		if cfg.command in optional_parameters:
			command = optional_parameters[cfg.command]
			if command == cfg.raise_command or command == cfg.lower_command:
				data['brightness'] = cfg.lights_commands[command]
			else:
				data['power'] = cfg.lights_commands[command]
		elif cfg.color in optional_parameters:
			data['color'] = optional_parameters[cfg.color]

		if not data:
			return

		self.publish(target_id, json.dumps(data))

	def publish(self, target_id, data):
		print("Publishing: " + str(target_id) + " " + str(data))
		self.publishers[target_id].publish(data)

	def stop(self):
		self.running = False
