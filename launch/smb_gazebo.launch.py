from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Include the main gazebo launch file
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("smb_gazebo"),
                "launch",
                "gazebo.launch.py"
            ])
        )
    )

    # Kinematics controller node
    kinematics_controller = Node(
        package="smb_kinematics_ros2",
        executable="smb_kinematics_ros2_node",
        name="smb_kinematics_ros2_node",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    # Low-level gazebo controller node
    low_level_controller = Node(
        package="smb_low_level_controller_gazebo_ros2",
        executable="smb_low_level_controller_gazebo_ros2_node",
        name="smb_low_level_controller_gazebo_ros2_node",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )
    
    joy_to_cmd_vel = Node(
        package="smb_kinematics_ros2",
        executable="smb_cmd_vel",
        name="smb_cmd_vel",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )
    
    joy = Node(
        package="joy",
        executable="joy_node",
        name="joy_node",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    return LaunchDescription([
        gazebo_launch,
        kinematics_controller,
        low_level_controller,
        joy_to_cmd_vel,
        joy,
    ])