import environment_config as cfg
import rospy
import threading
import traceback

from std_msgs.msg import Int32


class BlindsActuator:
	def __init__(self):
		self.running = False
		self.publishers = {}
		self.timers = {}
		for target_id, topic in cfg.blinds_topics.items():
			self.publishers[target_id] = rospy.Publisher(target_id, Int32, queue_size=10)
			self.timers[target_id] = None

	def process_command(self, optional_entities=None, on_success=None, on_fail=None):
		self.running = True
		if not optional_entities or cfg.command not in optional_entities:
			self.running = False
			if on_fail:
				on_fail()
			return
		try:
			if cfg.target_id in optional_entities:
				if optional_entities[cfg.target_id] in cfg.blinds_topics:
					self.run_command(
						optional_entities[cfg.target_id],
						cfg.blinds_commands[optional_entities[cfg.command]],
						on_success
					)
			else:
				for topic_id in cfg.blinds_topics.keys():
					self.run_command(
						topic_id,
						cfg.blinds_commands[optional_entities[cfg.command]],
						on_success
					)
		except Exception as e:
			print("Thrown exception: " + str(optional_entities) + " " + str(e))
			traceback.print_exc()
			if on_fail:
				on_fail()

	def on_timeout(self, target_id, on_success):
		self.timers[target_id] = None
		self.publish(target_id, cfg.blinds_commands[cfg.stop_command])
		for target in self.timers.keys():
			if self.timers[target]:
				return
		self.running = False
		if on_success:
			on_success()

	def run_command(self, target_id, command, on_success=None):
		self.publish(target_id, command)
		self.timers[target_id] = threading.Timer(cfg.blinds_actuation_seconds, self.on_timeout, [target_id, on_success])
		self.timers[target_id].start()

	def publish(self, target_id, command):
		self.publishers[target_id].publish(command)

	def stop(self):
		self.running = False
		for target_id in self.timers.keys():
			if self.timers[target_id]:
				self.timers[target_id].cancel()
			self.timers[target_id] = None
			self.publish(target_id, cfg.blinds_commands[cfg.stop_command])

