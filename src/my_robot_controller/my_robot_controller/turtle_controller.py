#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from turtlesim.srv import SetPen
from functools import partial

class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        self.previous_x = 0
        self.cmd_vel_publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_subscriber = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)
        self.get_logger().info('Turtle controller node has been started.')

    def pose_callback(self, pose: Pose):
        cmd = Twist()
        if pose.x > 9.0 or pose.x < 2.0 or pose.y > 9.0 or pose.y < 2.0:
            cmd.linear.x = 1.0
            cmd.angular.z = 0.9
        else:
            cmd.linear.x = 5.0
            cmd.angular.z = 0.0
        self.cmd_vel_publisher.publish(cmd)
        
        if pose.x > 5.5 and self.previous_x <= 5.5:
            self.previous_x = pose.x
            self.get_logger().info('Turtle is in the right half of the screen. Setting pen to red.')
            self.call_set_pem_service(255, 0, 0, 5, False)  
        elif pose.x <= 5.5 and self.previous_x > 5.5:
            self.previous_x = pose.x
            self.get_logger().info('Turtle is in the left half of the screen. Setting pen to blue.')
            self.call_set_pem_service(0, 0, 255, 5, False)  
        
        
    def call_set_pem_service(self,r,g,b,width,off):
        client = self.create_client(SetPen, '/turtle1/set_pen')
        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('Waiting for /turtle1/set_pen service...')
        request = SetPen.Request()
        request.r = r
        request.g = g
        request.b = b
        request.width = width
        request.off = off
        future = client.call_async(request)
        future.add_done_callback(partial(self.callback_set_pen))
        
    def callback_set_pen(self, future):
        try:
            response = future.result()
            self.get_logger().info('Set pen service called successfully.')
        except Exception as e:
            self.get_logger().error(f'Set pen service call failed: {e}')
        
        
def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()
    rclpy.spin(node)
    rclpy.shutdown()