from std_msgs.msg import ColorRGBA

# Map colors to display.
colors = {'person_color': ColorRGBA(0.0, 0.5, 0.5, 1.0),
		  'object_color': ColorRGBA(1.0, 1.0, 0.5, 1.0),
		  'qrcode_color': ColorRGBA(1.0, 0.5, 0.5, 1.0),
		  'person_default_color': ColorRGBA(0.2, 0.6, 1.0, 1.0)}

# Minimum euclidian distance between two objects of same class to be different.
objects_distance_threshold = 1.0