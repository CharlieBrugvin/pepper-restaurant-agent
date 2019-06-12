# Actuators target names
blinds_target_name = "blinds"
lights_target_name = "lights"

# Blinds actuation time
blinds_actuation_seconds = 3

stop_command = "stop"
raise_command = "raise"
lower_command = "lower"
on_command = "on"

# Actuators IDs and topics
blinds_topics = {
	"blinds_1": "/blinds_1",
	"blinds_2": "/blinds_2",
}

blinds_commands = {
	raise_command	: 1,
	stop_command	: 0,
	lower_command	: -1,
}

lights_topics = {
	"lights_1": "/lights_1",
}

lights_commands = {
	on_command		: "on",
	stop_command	: "off",
	raise_command	: 1,
	lower_command	: -1,
}

# Entity name for identifying the actuator.
target_id = "target_id"
command = "command"
color = "color"

optional_parameters = {
	"blinds": [],
	"lights": ["color"],
}
