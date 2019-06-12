import config as cfg
import math
import navigation.navigation_config as navig_cfg
import os.path
import pickle
import random
import rospy
import tf
import tf2_ros
import threading
import time

from actionlib_msgs.msg import GoalStatusArray, GoalID
from copy import deepcopy
from enum import Enum
from geometry_msgs.msg import Pose, PoseStamped, Vector3
from move_base_msgs.msg import MoveBaseActionFeedback, MoveBaseActionResult
from navigation.target import Target
from robot_localization import PepperLocalization
from scipy.spatial import distance
from std_msgs.msg import Header
from visualization_msgs.msg import Marker, MarkerArray


class ClassType(Enum):
	PERSON = 1
	OBJECT = 2
	QRCODE = 3
	PERSON_DEFAULT = 4


class NavigationManager:
	def __init__(self):
		self.pepper_localization = PepperLocalization()

		if cfg.robot_stream:
			self.marker_array_publisher = rospy.Publisher('/detections', MarkerArray, queue_size=100)
			self.move_publisher = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)

			self.cancel_publisher = rospy.Publisher('/move_base/cancel', GoalID, queue_size=10)
			self.feedback_subscriber = rospy.Subscriber('/move_base/feedback', MoveBaseActionFeedback, self.get_move_feedback)
			self.result_subscriber = rospy.Subscriber('/move_base/result', MoveBaseActionResult, self.get_move_action_result)
			self.status_subscriber = rospy.Subscriber('/move_base/status', GoalStatusArray, self.get_move_action_status)

		self.map_pose = None
		self.object_ID = 0
		self.encountered_positions = {}
		self.possible_goals = []
		self.on_success = None
		self.on_fail = None
		self.listener = tf.TransformListener()
		self.goal_ids = []
		self.move_action_feedback = None
		self.timer = None

	def get_move_action_status(self, data):
		if data:
			for status in data.status_list:
				self.goal_ids.append(status.goal_id)

	def get_move_action_result(self, data):
		if self.on_success:
			if data.status.status != 2:  # Goal canceled.
				if data.status.status == 3:  # Move completed.
					self.on_success()
				else:
					self.on_fail()
			self.clear_move_attrs()

	def clear_move_attrs(self):
		self.on_success = None
		self.on_fail = None

	def get_move_feedback(self, data):
		self.move_action_feedback = data

	def add_new_possible_goal(self, goal):
		self.possible_goals.append(goal)

	def move_to_coordinate(self, goal, on_success=None, on_fail=None):
		if cfg.robot_stream:
			goal_position = goal.pose.position
			robot_position = self.pepper_localization.get_pose().pose.position

			if robot_position:
				angle = math.atan2(goal_position.y - robot_position.y, goal_position.x - robot_position.x)

				old_angles = tf.transformations.euler_from_quaternion((goal.pose.orientation.x, goal.pose.orientation.y,
																	  goal.pose.orientation.z, goal.pose.orientation.w))
				q = tf.transformations.quaternion_from_euler(old_angles[0], old_angles[1], angle)
				goal.pose.orientation.x = q[0]
				goal.pose.orientation.y = q[1]
				goal.pose.orientation.z = q[2]
				goal.pose.orientation.w = q[3]

			self.move_publisher.publish(goal)
			self.on_success = on_success
			self.on_fail = on_fail
		else:
			self.timer = threading.Timer(10, self.on_timeout, [on_success, on_fail])
			self.timer.start()

	def stop_movement(self):
		if cfg.robot_stream:
			for goal_id in self.goal_ids:
				self.cancel_publisher.publish(goal_id)
			self.goal_ids = []
		else:
			if self.timer:
				self.timer.cancel()
			self.timer = None

	def is_located(self, key):
		return key in self.encountered_positions or key + '@' in self.encountered_positions

	def get_closest_location(self, locations):
		start_time = time.time()
		min_dist = 100000
		closest_location = None
		if cfg.robot_stream:
			robot_last_pose = self.pepper_localization.get_pose()
		else:
			robot_last_pose = PoseStamped()
		for location in locations:
			dist = self.compute_euclidian_distance(robot_last_pose.pose.position, location.pose.position)
			if dist < min_dist:
				min_dist = dist
				closest_location = location

		if cfg.debug_mode:
			print("\tget location %s seconds" % (time.time() - start_time))

		return closest_location

	def get_coordinate_for_label(self, key):
		if key in self.encountered_positions:
			return self.get_closest_location(self.encountered_positions[key][1:])
		elif key + "@" in self.encountered_positions:
			return self.get_closest_location(self.encountered_positions[key + "@"][1:])
		else:
			return None

	def compute_euclidian_distance(self, p1, p2):
		a = (p1.x, p1.y, p1.z)
		b = (p2.x, p2.y, p2.z)
		return distance.euclidean(a, b)

	def show_positions(self, data, value):
		targets = []
		if value == 'people':
			for info in data:  # info = [id, position, name]
				if len(info) > 2:
					show_target = Target(
						class_type=ClassType.PERSON,
						label=info[2],
						coordinates=info[1]
					)
					targets.append(show_target)

		elif value == 'qrcodes':
			for (label, position) in data:  # info = [label, position]
				show_target = Target(
					class_type=ClassType.QRCODE,
					label=label,
					coordinates=position
				)
				targets.append(show_target)

		elif value == 'objects':
			for (label, position) in data:  # info = [label, position]
				show_target = Target(
					class_type=ClassType.OBJECT,
					label=str(label),
					coordinates=position
				)
				targets.append(show_target)

		self.show_targets(targets)

	def show(self, people_3d_positions, objects_3d_positions, qrcodes_3d_positions):
		if cfg.debug_mode:
			start_time = time.time()

		self.show_positions(people_3d_positions, 'people')
		self.show_positions(objects_3d_positions, 'objects')
		self.show_positions(qrcodes_3d_positions, 'qrcodes')

		if cfg.debug_mode:
			show_time = time.time()
			print("\t markers - %s seconds" % (show_time - start_time))
		if cfg.show_markers:
			self.publish_positions()
		if cfg.debug_mode:
			print("\t publish - %s seconds" % (time.time() - show_time))

	def publish_positions(self):
		markers = []
		i = 0
		for label in self.encountered_positions:
			for position in self.encountered_positions[label][1:]:
				marker = Marker(
					type=Marker.TEXT_VIEW_FACING,
					id=i,
					lifetime=rospy.Duration(2.0),
					pose=deepcopy(position.pose),
					scale=Vector3(0.2, 0.2, 0.2),
					header=Header(frame_id='odom'),
					color=navig_cfg.colors[self.encountered_positions[label][0]],
					text=label)
				markers.append(marker)
				i += 1
				marker.pose.position.z += 0.3
				marker2 = Marker(
					type=Marker.SPHERE,
					id=i,
					lifetime=rospy.Duration(2.0),
					pose=position.pose,
					scale=Vector3(0.2, 0.2, 0.2),
					header=Header(frame_id='odom'),
					color=navig_cfg.colors[self.encountered_positions[label][0]],
					text=label
				)
				markers.append(marker2)
				i += 1

		if cfg.robot_stream:
			self.marker_array_publisher.publish(markers)

	def show_targets(self, targets, use_laser=True):
		try:
			if cfg.robot_stream:
				self.listener.waitForTransform('/laser', '/map', rospy.Time(), rospy.Duration(0.2))
		except (tf2_ros.TransformException, tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
			pass
		for target in targets:
			self.show_target(target, self.listener, use_laser)

	def show_target(self, target, listener, use_laser=True):
		if cfg.robot_stream:
			robot_last_pose = self.pepper_localization.get_pose()
		else:
			robot_last_pose = PoseStamped()
		if not robot_last_pose:
			return

		loc = Pose()
		loc.position.x = target.coordinates[0]
		loc.position.y = target.coordinates[1]
		loc.position.z = target.coordinates[2]
		loc.orientation = robot_last_pose.pose.orientation
		pose = PoseStamped()

		if use_laser:
			pose.header.frame_id = 'laser'
		else:
			pose.header.frame_id = 'map'
		pose.pose = loc

		if cfg.robot_stream:
			pose_in_map = listener.transformPose('/odom', pose)
		else:
			pose_in_map = pose
		pose_in_map.header.frame_id = 'odom'

		start_time = time.time()

		if target.class_type == ClassType.OBJECT:
			matched = False
			if target.label in self.encountered_positions:
				for existing_position in self.encountered_positions[target.label][1:]:
					if self.compute_euclidian_distance(existing_position.pose.position,
							pose_in_map.pose.position) < navig_cfg.objects_distance_threshold:
						matched = True
				if not matched:
					self.encountered_positions[target.label].append(pose_in_map)
			else:
				self.encountered_positions[target.label] = ['object_color', pose_in_map]
				self.add_new_possible_goal(target.label)

		else:
			if not target.label in self.encountered_positions:
				self.encountered_positions[target.label] = ['qrcode_color', pose_in_map]
				if target.class_type == ClassType.PERSON:
					self.encountered_positions[target.label][0] = 'person_color'
				elif target.class_type == ClassType.PERSON_DEFAULT:
					self.encountered_positions[target.label][0] = 'person_default_color'
				self.add_new_possible_goal(target.label)
			else:
				self.encountered_positions[target.label][1] = pose_in_map

		if cfg.debug_mode:
			print("\ttransform %s seconds" % (time.time() - start_time))

	def load_default_positions(self):
		targets = []
		for key, value in cfg.default_positions.iteritems():
			show_target = Target(
				class_type=ClassType.PERSON_DEFAULT,
				label=key + '@',
				coordinates=value
			)
			targets.append(show_target)
		self.show_targets(targets, False)

	def load_positions_from_file(self):
		if not os.path.isfile(cfg.last_known_positions_file):
			return

		with open(cfg.last_known_positions_file, 'r') as content_file:
			self.encountered_positions = pickle.load(content_file)

	def save_positions_to_file(self):
		with open(cfg.last_known_positions_file, 'w') as content_file:
			stable_targets = {}
			for key, target in self.encountered_positions.iteritems():
				if target[0] == 'person_color' or target[0] == 'qrcode_color':
					stable_targets[key] = target
			pickle.dump(stable_targets, content_file)

	def shut_down(self):
		self.save_positions_to_file()

	def on_timeout(self, on_success, on_fail):
		self.timer = None
		if random.random() < 0.5:
			if on_success:
				on_success()
		else:
			if on_fail:
				on_fail()


