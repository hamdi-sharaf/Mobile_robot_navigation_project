#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
from std_srvs.srv import Empty, EmptyRequest
import time
import math

class MoveHokuyoLaserRobot():
    
    def __init__(self):
        
        # Init Publisher
        self.hokuyo_laser_robot_vel_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.cmd = Twist()
        # Init Subscriber
        self.amcl_pose_sub = rospy.Subscriber('/amcl_pose', PoseWithCovarianceStamped, self.sub_callback)
        self.sub_msg = PoseWithCovarianceStamped()
        # Initialize Service Client
        rospy.wait_for_service('/global_localization')
        self.disperse_particles_service = rospy.ServiceProxy('/global_localization', Empty)
        self.srv_request = EmptyRequest()
        # Other stuff
        self.ctrl_c = False
        rospy.on_shutdown(self.shutdownhook)
        self.rate = rospy.Rate(10)
        
    def shutdownhook(self):
        
        # works better than the rospy.is_shut_down()
        self.stop_hokuyo_laser_robot()
        self.ctrl_c = True

    def stop_hokuyo_laser_robot(self):
        
        rospy.loginfo("Shutdown time! Stop the robot")
        self.cmd.linear.x = 0.0
        self.cmd.angular.z = 0.0
        i = 0
        
        while i < 20:
            self.hokuyo_laser_robot_vel_publisher.publish(self.cmd)
            self.rate.sleep()
            i += 1

    def move_forward(self, linear_speed=0.3, angular_speed=0.0):
        
        self.cmd.linear.x = linear_speed
        self.cmd.angular.z = angular_speed
        i = 0
        
        while i < 50:
            self.hokuyo_laser_robot_vel_publisher.publish(self.cmd)
            self.rate.sleep()
            i += 1
        
    def turn(self, linear_speed=0.0, angular_speed=0.8):
        
        self.cmd.linear.x = linear_speed
        self.cmd.angular.z = angular_speed
        i = 0
        
        while i < 25:
            self.hokuyo_laser_robot_vel_publisher.publish(self.cmd)
            self.rate.sleep()
            i += 1
    
    def move_square(self):
        
        i = 0
        
        while not self.ctrl_c and i < 4:
            # Move Forwards
            rospy.loginfo("######## Going Forwards...")
            self.move_forward()
            self.stop_hokuyo_laser_robot()
            # Turn
            rospy.loginfo("######## Turning...")
            self.turn()
            self.stop_hokuyo_laser_robot()
            i += 1
            
        self.stop_hokuyo_laser_robot()
        rospy.loginfo("######## Finished Moving in a Square")
        
    def call_service(self):
        
        rospy.loginfo("######## Calling Service...")
        result = self.disperse_particles_service(self.srv_request)
        
    def sub_callback(self, msg):
        
        self.sub_msg = msg

    def calculate_covariance(self):
        
        rospy.loginfo("######## Calculating Covariance...")
        cov_x = self.sub_msg.pose.covariance[0]
        cov_y = self.sub_msg.pose.covariance[7]
        cov_z = self.sub_msg.pose.covariance[35]
        rospy.loginfo("## Cov X: " + str(cov_x) + " ## Cov Y: " + str(cov_y) + " ## Cov Z: " + str(cov_z))
        cov = (cov_x+cov_y+cov_z)/3
        
        return cov
        
            
if __name__ == '__main__':
    rospy.init_node('move_hokuyo_laser_robot_node', anonymous=True)
    MoveHokuyoLaserRobot_object = MoveHokuyoLaserRobot()
    
    cov = 1
    
    while cov > 0.65:
        MoveHokuyoLaserRobot_object.call_service()
        MoveHokuyoLaserRobot_object.move_square()
        cov = MoveHokuyoLaserRobot_object.calculate_covariance()
        rospy.loginfo("######## Total Covariance: " + str(cov))
        if cov > 0.65:
            rospy.loginfo("######## Total Covariance is greater than 0.65. Repeating the process...")
        else:
            rospy.loginfo("######## Total Covariance is lower than 0.65. Robot correctly localized!")
            rospy.loginfo("######## Exiting...")
        
    
    
