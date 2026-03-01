# Cornell Aerospace Adversary Lab - Magpie Project 
The following outline some of the many pipelines involved in the Magpie Project as part of Cornell University's Aerospace Adversary Lab. 

## Marvelmind GPS Subscription
Using Marvelmind Robotic's GPS setup and following their video below, along with their posted guidelines on positioning the beacons, we were able to develop an in-houses test-bed: 

[Marvelmind System Unpacking](https://marvelmind.com/pics/Marvelmind_Robotics_ENG_placement_manual.pdf)


[Marvelmind Beacon Arrangement](https://www.youtube.com/watch?v=Uj2_BGS1AjI)


From the video, download the latest stable SW and API; unzip the files; then navigate to the Dashboard folder, then once inside the Dashboard folder navigate to the appropriate folder for your particular system (e.g. Linux). Follow the embedded pdf (e.g. "dashboard_linux_manual_v2019_05_14.pdf") in the aforementioned folder. Copy the dashboard and dashboard API to the directory you will use for the program: 

```
sudo cp libdashapi.so/usr/local/lib

sudo ldconfig
```
Then, if you need to give rights for the serial port access: 
```
sudo adduser $USER dialout

KERNEL==”ttyACM0” GROUP=”dialout”, MODE=”666”
```
Then, setup the permissions to execute the dashboard: 
```
sudo chmod 0777 ./dashboard_x86
```

Then, beacon by beacon, plug into your machine and navigate to the upper toolbar in the Dashboard underneath "Firmware", then "Upload firmware", flash with the most recent SW file for each beacon and for each modem (e.g. "Modem_hw51" for the modem or "NIA_2024_05_08_Super_Beacon_915.hex"). For our particular case, the NIA (Non-Inverse Architecture) was the most stable, so we made sure to keep that architecture consistent across all devices. 

After following the directions for placing the beacons linked above, creating the submap referenced in the video linked above, and testing in the Dashboard, we were prepared to start testing the system more rigorously. 

### Marvelmind Position Querying
Pull the following Python script developed by Marvelmidn and slightly adjusted by myself:
[Marvelmind Raw Python Script](https://github.com/MarvelmindRobotics/marvelmind.py/blob/master/src/marvelmind.py)

Then, save the python script in the same folder as the following: 

[Marvelmind Positional Graphing](https://github.com/JonathanDistler/MarvelmindModularization/blob/main/Position.py)

Figure out the port the modem is connected too (e.g. ACM0), make sure that is the same port reflected in the "Marvelmind Raw Python Script" underneath the "_init_" function in the MarvelmindHedge class. 

Now, you can query the position of a mobile beacon (known in Marvelmind as a hedgehog). As an important side-note, the positional querying cannot happen at the  same time the dashboard is open. 

Additionally, one can follow the following script that uses an output CSV file to graph position over time, rather than a pure line-graph:

[Marvelmind Positional Graphing - 3D](https://github.com/JonathanDistler/MarvelmindModularization/blob/main/3DMatlabGraph.m)

## Marvelmind ROS 2 Publisher and Subscriber
For future work in swarm-drone tactics, ROS 2 is far and ahead the best method, so we also developed methods to query in real-time with ROS 2 pub-sub architecture. 

First, to setup the ROS 2 workspace do the following: 

```
mkdir -p ~/gps_ws/src
cd ~/gps_ws
colcon build
```

We had issues creating a package to publish the positional data, so we concatenated two libraries on top of each other in the following subscriber: 

[Marvelmind ROS 2 Subscriber](https://docs.google.com/document/d/1ff4DUxiCMj8-jBYLdYZq3IawdXlIeO-HAD4Mr4BNwYw/edit?tab=t.0)

After saving the subscriber in the workspace, one can execute the following lines in terminal to query Marvelmind data (below is our folder specific version):

```
cd ~/gps_ws
source install/setup.bash
ros2 run gps_listener listener
```

### Gazebo Telemetry Data
In addition to the hardware pipeline involving Marvelmind, we also implemented a Gazebo and PX4 simulation setup using the following steps provided by Cameron Mehlman: 

First, install Gazeb: 

[Gazebo Downloads Page](https://gazebosim.org/docs/harmonic/install_ubuntu/)

Then, clone the PX4 repo:
```
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
```
Then, build the simulation. This step takes some time, so it is beneficial to do so headless: 
```
make px4_sitl gz_x500

or 

HEADLESS=1 make px4_sitl gz_x500 
```
Then, run QGroundControl such that PX4 thinks all preflight requirements have been checked; this doesn't need to be run if PyMavLink is being used to engage offboard mode

If QGroundControl is not installed, do so via the link below: 

[QGroundControl Download](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-user-guide/getting_started/download_and_install.html)

QGroundControl (QGC) must be run with a GUI, if only using a terminal version, one has to use MAVProxy. 

Then, use the following pipeline to begin the simulation: 

Create a small script using the following for MAVProxy, but this isn't super necessary for the newest ROS2 implementation:

```
from pymavlink import mavutil

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')

master.wait_heartbeat()

print("Heartbeat received. PX4 preflight checks should now pass.")
```
Then, begin the simulation with the following, and then execute the script in another terminal:

```
pip install MAVProxy

mavproxy.py --master=udp:127.0.0.1:14550 #needs to always be running in background

```

The entire pipeline by terminal is below, for our specific use-case: 

Terminal 1:
```
cd Distler_PX4/PX4-Autopilot
HEADLESS=1 make px4_sitl gz_x500
```

Terminal 2:
```
cd Distler_PX4/PX4-Autopilot
mavproxy.py –master=udp:127.0.0.1:14550
```

Terminal 3:
```
cd ros2_ws
ros2 run mavsdk_ros2 mavsdk_command_node
```

Terminal 4:
```
cd ros2_ws
ros2 run mavsdk_ros2 mavsdk_listener_node
```

For a more robust pipeline, I altered the code for MAVProxy to include the following publisher and subscriber:

[Updated MAVProxy Publisher/Command Node](https://docs.google.com/document/d/1JHlRdq3NmeFowFI05NDhqTYWgTJsKXut19HwBZDTvFM/edit?tab=t.0)

[Updated MAVProxy Subscriber/Listener Node](https://docs.google.com/document/d/15eTmoMGFl5qXzEIpzZWYzqegKElGrSda8khJXOhGZ_I/edit?tab=t.0)
