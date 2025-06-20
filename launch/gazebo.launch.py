from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    IfElseSubstitution,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Declare all launch arguments
    
    world_file_path = PathJoinSubstitution([
        FindPackageShare("smb_gazebo"),
        "worlds",
        LaunchConfiguration("world_file"),
    ])
    
    declared_arguments = [
        DeclareLaunchArgument(
            "world_file",
            default_value="warehouse.world",
            description="Path to the world file",
        ),
        DeclareLaunchArgument("x", default_value="0.0"),
        DeclareLaunchArgument("y", default_value="0.0"),
        DeclareLaunchArgument("z", default_value="0.25"),
        DeclareLaunchArgument("yaw", default_value="0.0"),
        DeclareLaunchArgument("paused", default_value="false"),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument("debug", default_value="false"),
        DeclareLaunchArgument("verbose", default_value="false"),
        DeclareLaunchArgument("run_gui", default_value="true"),
    ]

    # Include the existing load.launch.py
    load_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("smb_description"),
                "launch",
                "load.launch.py"
            ])
        ])
    )

    # # Gzserver
    # gzserver = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         PathJoinSubstitution(
    #             [FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]
    #         )
    #     ),
    #     launch_arguments={
    #         "gz_args": [
    #             "-s ",
    #             IfElseSubstitution(
    #                 LaunchConfiguration("paused"), if_value="", else_value="-r "
    #             ),
    #             IfElseSubstitution(
    #                 LaunchConfiguration("verbose"), if_value="-v4 ", else_value=""
    #             ),
    #             LaunchConfiguration("world_file"),
    #         ],
    #         "on_exit_shutdown": "true",
    #     }.items(),
    # )

    # # Gzclient
    # gzclient = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         PathJoinSubstitution(
    #             [FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]
    #         )
    #     ),
    #     launch_arguments={
    #         "gz_args": [
    #             "-g ",
    #             IfElseSubstitution(
    #                 LaunchConfiguration("verbose"), if_value="-v4 ", else_value=""
    #             ),
    #         ],
    #     }.items(),
    #     condition=IfCondition(LaunchConfiguration("run_gui")),
    # )
    
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"])
        ),
        launch_arguments={
            "gz_args": [
                IfElseSubstitution(LaunchConfiguration("paused"), if_value="", else_value="-r "),
                IfElseSubstitution(LaunchConfiguration("verbose"), if_value="-v4 ", else_value=""),
                # LaunchConfiguration("world_file"),
                world_file_path,
            ],
            "on_exit_shutdown": "true",
        }.items(),
    )

    # Spawn robot model
    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "robot_description",  # Use the topic from load.launch.py
            "-name", "smb",
            "-x", LaunchConfiguration("x"),
            "-y", LaunchConfiguration("y"),
            "-z", LaunchConfiguration("z"),
            "-Y", LaunchConfiguration("yaw"),
        ],
        output="screen",
    )

    # ros_gz_bridge config
    ros_gz_bridge_config = PathJoinSubstitution([
        FindPackageShare("smb_gazebo"), "config", "smb_gz_bridge.yaml"
    ])

    ros_gz_bridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("ros_gz_bridge"), "launch", "ros_gz_bridge.launch.py"
            ])
        ),
        launch_arguments={
            "bridge_name": "ros_gz_bridge",
            "config_file": ros_gz_bridge_config,
        }.items(),
    )

    return LaunchDescription(
        declared_arguments
        + [
            load_launch,
            # gzserver,
            # gzclient,
            gz_sim,
            spawn_robot,
            ros_gz_bridge,
        ]
    )