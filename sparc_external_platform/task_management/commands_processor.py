import json
import rospy

from std_msgs.msg import String


class CommandsProcessor:
	def __init__(self, on_command_received):
		self.on_command_received = on_command_received
		self.commands_subscriber = rospy.Subscriber('/commands_structured', String, self.on_command)

	def on_command(self, received_data):
		command = json.loads(received_data.data)
		if command:
			self.on_command_received(command)


if __name__ == '__main__':
	def print_data(data):
		print(data)

	CommandsProcessor(print_data)
