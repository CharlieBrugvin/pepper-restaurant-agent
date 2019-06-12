# Use robot sensors for running the system.
robot_stream = True
external_camera = -1

# Use audio stream for commands.
audio_stream = False

# Receive external commands.
receive_commands = True

# Robot information.
ip = '192.168.0.115'
port = 9559
frameRate = 30

# Show debug info.
debug_mode = False
show_markers = True
display_images = True

# Language information.
language_en = 'en-EN'
language_ro = 'ro-RO'
language = language_ro

# Project path.
project_path = '/home/sparc-308/workspace/sparc/'

# Folder to save new people.
new_people_path = '/home/sparc-308/workspace/sparc/external_platform/vision/facenet/out_dir/'

# NaoQI path.
naoqi_path = '/home/sparc-308/workspace/stefania/pynaoqi-python2.7/lib/python2.7/site-packages'

last_known_positions_file = 'positions.p'

default_positions = {
	'alex': [5.7, 6.2, 1],
	'stephanie': [6.0, 6.7, 1],
	'home': [5.5, 10.0, 0]
}
