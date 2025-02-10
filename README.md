# Walter
## The ecuadorian service robot
In this work is the simulation of Walter, a robor develop in ESPOL (Ecuador). It is a mobile robot which is focus in the social navigation field, playing many different roles as server, host, AVG. 

+ Nowadays is using ROS2 humble
+ For running the code you need the three repo above:
  - https://github.com/JrLuimira/walter_cartographer.git
  - https://github.com/JrLuimira/walter_navigation.git
    
## The steps to run the simulation:
# 1. It is important to start the robot model. So in this case the next launch is about to show a pre modeled world in Gazebo:
```python 
ros2 launch walter_description gazebo_walter.launch.py x:=1.0 y:=0.4 z:=0.2
```

# 2. Now it is important to upload the cartographer launch for making the online navigation:
```python 
ros2 launch walter_cartographer cartographer.launch.py
```

# 3. As a final step, we upload the navigation launch which contains the RVIZ config to see how the robot navigates.
```python 
ros2 launch walter_navigation navigation walter_navigation.launch.py
```

