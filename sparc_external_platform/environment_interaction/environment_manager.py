import environment_config as cfg

from blinds import BlindsActuator
from lights import LightsActuator


class EnvironmentManager:
	def __init__(self):
		self.blinds_actuator = BlindsActuator()
		self.lights_actuator = LightsActuator()

	def process_command(self, target, optional_entities=None, on_success=None, on_fail=None):
		if target == cfg.blinds_target_name:
			if not self.blinds_actuator.running:
				self.blinds_actuator.process_command(optional_entities, on_success, on_fail)
		elif target == cfg.lights_target_name:
			if not self.lights_actuator.running:
				self.lights_actuator.process_command(optional_entities, on_success, on_fail)
		else:
			print("%s: Not a valid actuator." % self.__class__.__name__)
			on_fail()

	def stop(self):
		if self.blinds_actuator.running:
			self.blinds_actuator.stop()
		elif self.lights_actuator.running:
			self.lights_actuator.stop()
