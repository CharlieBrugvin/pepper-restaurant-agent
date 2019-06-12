import config as cfg
import numpy as np
import rospy
import tf

from actionlib_msgs.msg import GoalStatusArray
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav_msgs.msg import OccupancyGrid
from std_msgs.msg import String


class PepperLocalization:
    def __init__(self):
        if cfg.robot_stream:
            rospy.Subscriber('/slam_out_pose', PoseStamped, self.update_pose)
            rospy.Subscriber('/amcl_pose', PoseWithCovarianceStamped, self.update_pose)
            rospy.Subscriber('/map', OccupancyGrid, self.update_map)
        self.map = None
        self.latest_pose = None
        self.latest_map = None
        self.latest_map_pose = None
        self.listener = tf.TransformListener()

    def get_pose(self):
        return self.latest_pose

    def update_pose(self, data):
        if type(data) is PoseWithCovarianceStamped:
            self.latest_pose = data.pose
        else:
            self.latest_pose = data

    def update_map(self, data):
        self.map = data
        self.map_width = data.info.width
        self.map_height = data.info.height
        self.resolution = data.info.resolution

        if(self.latest_pose and self.latest_pose.pose):
            x = int(self.map_width / 2 + self.latest_pose.pose.position.x / self.resolution)
            y = int(self.map_height / 2 + self.latest_pose.pose.position.y / self.resolution)
            self.latest_map_pose = (x, y)
        data.data = [50 if x==-1 else x for x in data.data]
        self.latest_map = np.array([255 - i*2.55 for i in data.data]).reshape(data.info.width, data.info.height)
