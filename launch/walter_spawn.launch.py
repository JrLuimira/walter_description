from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import (
    Command,
    FindExecutable,
    PathJoinSubstitution,
    LaunchConfiguration,
)
from launch.event_handlers import OnProcessExit
from launch.actions import TimerAction


def generate_launch_description():

    walter_description_dir = FindPackageShare(package="walter_description").find(
        "walter_description"
    )

    # ! PARAMETERS
    x_arg = DeclareLaunchArgument("x", default_value="0", description="X position")
    y_arg = DeclareLaunchArgument("y", default_value="0", description="Y position")
    z_arg = DeclareLaunchArgument("z", default_value="0.05", description="Z position")

    # Define the robot_description parameter using xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution([walter_description_dir, "urdf", "walter.xacro"]),
        ]
    )  # To be cleaned on issue #92
    # print(robot_description_content.perform(context=context))

    robot_description = {
        "robot_description": ParameterValue(robot_description_content, value_type=str),
    }

    # Node to spawn the model in Gazebo
    spawn_model_node = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        name="walter_spawn",
        output="screen",
        parameters=[{"robot_description": robot_description}],
        arguments=[
            "-entity",
            "walter",
            "-topic",
            "robot_description",
            "-x",
            LaunchConfiguration("x"),
            "-y",
            LaunchConfiguration("y"),
            "-z",
            LaunchConfiguration("z"),
        ],
    )

    # Load the controllers from the YAML file
    joint_state_broadcaster_spawner_node = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
    )

    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_drive_base_controller",
            "--controller-manager",
            "/controller_manager",
        ],
        remappings=[
            ("/diff_drive_base_controller/cmd_vel_unstamped", "/cmd_vel"),
        ],
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
    )

    delay_robot_controller_spawner_after_joint_state_broadcaster_spawner = (
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner_node,
                on_exit=[robot_controller_spawner],
            ),
        )
    )

    # ! LAUNCH DESCRIPTION DECLARATION
    ld = LaunchDescription()

    # ! DECLARE ARGUMENTS
    ld.add_action(x_arg)
    ld.add_action(y_arg)
    ld.add_action(z_arg)

    ld.add_action(spawn_model_node)
    ld.add_action(joint_state_broadcaster_spawner_node)
    ld.add_action(robot_controller_spawner)

    return ld
