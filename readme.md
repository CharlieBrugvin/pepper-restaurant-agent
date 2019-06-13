# Pepper restaurant agent

Pepper restaurant agent is a program for the [social robot Pepper](https://www.softbankrobotics.com/emea/en/pepper?q=emea/fr/pepper). When launched, Pepper waits to be called by a user. It will then meet him and engage a conversation to help him to find a restaurant in Cambridge. When the conversation is over, Pepper goes back to its initial place, and wait to be called by another user.

It uses ROS and the code is written in Python.
 
## System and dependencies

We use Ubuntu 16.04 LTS with ROS kinetic ([link](http://wiki.ros.org/ROS/Tutorials))

### Ros packages

#### Install `pepper_bringup` & `nao_audio` : 

- `pepper_bringup`, to access to pepper naoqi : installation instructions are on the [package page](http://wiki.ros.org/pepper_bringup?distro=kinetic).

- `nao_audio`, for the audio source localization ([package page](http://wiki.ros.org/nao_audio)) : Clone the [github repository](https://github.com/ros-naoqi/nao_interaction) into ros workspace & build.

#### Sparc external platforms

For the speech recognition, we use the `speech module` of [sparc](https://sparc.readthedocs.io/en/latest/welcome.html). We added a small feature (publish with transcript the timestamp of its listening).

The updated module is at [/sparc_external_platform/speech](/sparc_external_platform/speech).

### NNDIAL

NNDIAL ([github](https://github.com/shawnwun/NNDIAL)) is a dialog model. We run a pretrained LIDM dialog model on a local server in order to be requested by our `pepper_restaurant_agent` program.

------------------

## Launching *Pepper restaurant agent*

### Set Pepper

The autonomous life must be disabled and Pepper have to be awake.

With Choregraphe, in the top right corner :

- Disable autonomous life
    >  **heart** button : *turn off autonomous life*

- enable awake mode: 
    > **sun** button : *Wake Up*

### `roscore` & `pepper_bringup`

Run roscore :
```
roscore
```

Launch `pepper_bringup` in order to have acces to these topics :
- `/pepper_robot/naoqi_driver/audio` 
- `/speech`
- `/move_base_simple/goal`
- `/pepper_robot/naoqi_driver/sonar/front`

With your *Pepper IP address* :
```
roslaunch pepper_bringup pepper_full.launch nao_ip:=<robot_ip> roscore_ip:=<roscore_ip> [network_interface:=<eth0|wlan0|vpn0>]
```

### Pepper Speech Recognition

Go to the sparc speech module :
```
cd sparc_external_platform/speech
```
Run :
```
python run_nlp.py

```
And answer `yes` to use the pepper microphone :
```
Audio stream? [y/n]: y
```

It publishes on the topic `/commands_text`

### Audio source localization

Launch `nao_interaction_launchers` with yout *Pepper IP address* :
```
roslaunch nao_interaction_launchers nao_audio_interface.launch nao_ip:=<robot_ip> nao_port:=<robot_port>
```

It publishes on the topic `/nao_audio/audio_source_localization`

### NNDIAL on a server

Go to `NNDIAL-master` folder
```
cd .../NNDIAL-master/
```
Launch the pretrained LIDM model on a server :
```
python server.py -config config/demo/LIDM.cfg -mode interact
```

### Launch `pepper_restaurant_agent.py`

```
python pepper_restaurant_agent.py
```

Pepper will :
    
    1. Wait to be called
    2. Turn and move to the user
    3. Dialog with the user to give informations about Cambridge restaurants
    4. Go to it's initial place
    5. Wait to be called ...
