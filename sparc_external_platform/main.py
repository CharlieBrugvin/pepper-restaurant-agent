import config as cfg
import sys
sys.path.insert(0, cfg.naoqi_path)

import argparse
import qi
import rospy
import signal
import traceback
import time

from task_management.task_manager import TaskManager


class Main(object):
	def __init__(self, app):
		if cfg.robot_stream:
			app.start()
		if cfg.robot_stream	or cfg.receive_commands:
			rospy.init_node('listener', anonymous=True)

		self.task_manager = TaskManager(app)
		super(Main, self).__init__()

	def interuppt_handler(self, signum, frame):
		print('Forced interruption by user, shutting down...')
		self.terminate()
		sys.exit(-2)

	def terminate(self):
		self.task_manager.vision_manager.shut_down()
		self.task_manager.navigation_manager.shut_down()

	def run(self):
		print('Running...')
		print('Looking for objects...')
		self.task_manager.navigation_manager.load_positions_from_file()
		self.task_manager.navigation_manager.load_default_positions()

		if cfg.robot_stream:
			self.task_manager.pose_manager.stand_init()

		try:
			while self.task_manager.vision_manager.is_running():
				if cfg.debug_mode:
					start_time = time.time()
				people_3d_positions, objects_3d_positions, qrcodes_3d_positions = self.task_manager.vision_manager.detect()
				if cfg.debug_mode:
					vision_time = time.time()
					print("--- vision processing: \t %s seconds ---" % (vision_time - start_time))
				self.task_manager.navigation_manager.show(people_3d_positions, objects_3d_positions, qrcodes_3d_positions)
				if cfg.debug_mode:
					display_time = time.time()
					print("--- rviz display: \t %s seconds ---" % (display_time - vision_time))
				# if self.task_manager.current_task:
				# 	print('CTask: ' + str(self.task_manager.current_task))
				# if self.task_manager.ongoing_tasks:
				# 	print('Queue: '+ str(self.task_manager.ongoing_tasks))
				# 	print('')
				self.task_manager.step()
				if cfg.debug_mode:
					print("--- task execution: \t %s seconds ---" % (time.time() - display_time))
					print("\n")
			self.terminate()

		except KeyboardInterrupt:
			print('Forced interruption by user, shutting down...')
			self.terminate()

		except Exception as e:
			print('Thrown exception: ' + str(e))
			traceback.print_exc()
			self.terminate()


if __name__ == '__main__':
	application = None

	parser = argparse.ArgumentParser(description='Run the vision component.')
	parser.add_argument("-nr", "--not_robot_stream", help="Specify not to interact with the robot", action="store_true")
	args = parser.parse_args()

	if args.not_robot_stream:
		cfg.robot_stream = False

	if cfg.robot_stream:
		# Initialize robot's NAOqi framework.
		try:
			connection_url = 'tcp://' + cfg.ip + ':' + str(cfg.port)
			application = qi.Application(['Main', '--qi-url=' + connection_url])
		except RuntimeError:
			print('Can\'t connect to NAOqi at \'' + cfg.ip + ':'  + str(cfg.port) +'\'.\n'
				'Please check your script arguments. Run with -h option for help.')
			sys.exit(1)

	main = Main(application)
	signal.signal(signal.SIGINT, main.interuppt_handler)
	main.run()
