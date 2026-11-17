import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory('rover_description')
    xacro_file = os.path.join(pkg, 'urdf', 'rover.urdf.xacro')
    world = os.path.join(pkg, 'worlds', 'rover_world.sdf')

    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': f'-r {world}'}.items())

    rsp = Node(package='robot_state_publisher', executable='robot_state_publisher',
               parameters=[{'robot_description': robot_description,
                            'use_sim_time': True}])

    spawn = Node(package='ros_gz_sim', executable='create',
                 arguments=['-topic', 'robot_description', '-name', 'rover', '-z', '0.15'])

    bridge = Node(package='ros_gz_bridge', executable='parameter_bridge',
                  arguments=[
                      '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                      '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                      '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                      '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                      '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
                      '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
                      '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
                  ],
                  output='screen')

    return LaunchDescription([gz_sim, rsp, spawn, bridge])