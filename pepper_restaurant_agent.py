
import json
import time
import re
import requests # to request NNDIAL

from tf.transformations import quaternion_from_euler # used to rotate
from math import radians, degrees

import rospy
# ros messages
from std_msgs.msg import String # speak / hear
from nao_interaction_msgs.msg import AudioSourceLocalization # audio localization
from sensor_msgs.msg import Range # sonar
from geometry_msgs.msg import PoseStamped # move

# --------------------------- global constants -------------------------------
# ----------------------------------------------------------------------------

NNDIAL_URL = 'http://127.0.0.1:8000/'
AUDIO_LOCALIZATION_INTENSITY_TRESHOLD = 0.2
DISTANCE_TO_USER_DURGING_DIALOG = 0.50 # cm

# ---------------------------- global variables  -----------------------------
# ----------------------------------------------------------------------------

# the timestamp of the begining and the end of the last pepper speech
last_speech_start_date = last_speech_end_date = None

# ---------------------------- function utils --------------------------------
# ----------------------------------------------------------------------------

def console_log(message):
    print '[' + str(int(time.time())) + ']', message

# used when it is necessary to stop the program until a new topic value
def wait_new_value_of_local_topic(topic_name, log=True):
    if log: console_log("waiting for a new value on the topic '" + topic_name + "'")
    
    current_topic_value = local_topics[topic_name]
    while local_topics[topic_name] == current_topic_value:
        time.sleep(0.1)

    if log: console_log("new value of '" + topic_name + "' : '" + str(local_topics[topic_name]) + "'")
    return local_topics[topic_name]

def contains(text, word):
    return word.lower().replace(' ', '') in text.lower().replace(' ', '')

def request_nndial(request):
    console_log('request nndial on ' + NNDIAL_URL)
    r = requests.post(
        url=NNDIAL_URL,
        headers= {'Content-type': 'application/json'},
        data=json.dumps(request)
    )
    console_log('received nndial response')
    return json.loads(r.text)


# estimate the duration of pepper audio speech from text
def get_utterance_duration(text):
    # count number of words & digits
    nb_words = len(re.findall(r'[a-zA-Z]+', text))
    nb_digits = len(re.findall(r'[0-9]', text))

    # estimate duration
    word_duration = 0.40
    digit_duration = 0.40
    return  nb_words * word_duration  + nb_digits * digit_duration

# estimate the duration of a move
def get_move_duration(x, y, angle_degree):
     x_duration = 1 + abs(x)*5
     y_duration = 1 + abs(y)*5
     rotation_duration = 1.7 + abs(angle_degree) * 0.025

     return max([x_duration, y_duration, rotation_duration])

# ----------------------- ros topic trigger functions ------------------------
# ----------------------------------------------------------------------------

# local state (in the current program) of the ros topics
local_topics = {
    'audio_source_angle': None, # from /nao_audio/audio_source_localization
    'utterance_heard': None, # from /commands_text
    'distance_obstacle': None # from /pepper_robot/naoqi_driver/sonar/front
}

def on_new_audio_source_localization(new_value):
    # angle in degree
    azimuth_deg = round(degrees(new_value.azimuth.data), 2)
    if azimuth_deg > 181: azimuth_deg -= 360
    
    energy = round(new_value.energy.data, 2)
    if energy >= AUDIO_LOCALIZATION_INTENSITY_TRESHOLD:
        global local_topics
        local_topics['audio_source_angle'] = azimuth_deg

def on_new_utterance_heard(new_value):
    # we get text and date
    data = json.loads(new_value.data)
    utterance = data['text']
    speech_end_date = float(data['time_stop_speaking'])

    # if the utterance was recorded when pepper was speaking (with 1s margin), we drop it
    if not (last_speech_start_date <= speech_end_date <= last_speech_end_date + 1):
        global local_topics
        local_topics['utterance_heard'] = utterance
    else:
        console_log("heard '"+ utterance + "' but it is from Pepper.")

def on_new_sonar_distance(new_value):
    global local_topics
    local_topics['distance_obstacle'] = round(float(new_value.range), 2)

# -------------------------- ros topic publishers ----------------------------
# ----------------------------------------------------------------------------

# publish on /move_base_simple/goal
# Take the distance in centimeter on x and y , and the degree of rotation
def move(x=0, y=0, angle_degree=0):

    # we convert the z angle (in degree) in a quaternion form
    q = quaternion_from_euler(0, 0, radians(angle_degree))
    # we create the message to be published
    message = PoseStamped()
    message.header.seq = 1
    message.header.stamp = rospy.Time.now()
    message.header.frame_id = "base_footprint"
    message.pose.position.x = x
    message.pose.position.y = y
    message.pose.orientation.x = q[0]
    message.pose.orientation.y = q[1]
    message.pose.orientation.z = q[2]
    message.pose.orientation.w = q[3]

    # we publish with a new publisher
    pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=5, latch=True)
    pub.publish(message)

    # console log 
    if (x != 0):            console_log('x-axis move of ' + str(x) + ' m')
    if (y != 0):            console_log('y-axis move of ' + str(y) + ' m')
    if (angle_degree != 0): console_log('rotation of ' + str(angle_degree) + ' deg')

    # we quit the function when the move is over
    duration = get_move_duration(x, y, angle_degree)
    time.sleep(duration)
    
    console_log('move is done')

# publish on /speech
def speak(utterance):

    # we calculate the start and end timestamp of the speech
    duration_utterance = get_utterance_duration(utterance)
    global last_speech_start_date, last_speech_end_date
    last_speech_start_date = time.time()
    last_speech_end_date = time.time() + duration_utterance

    pub = rospy.Publisher('speech', String, queue_size=10, latch=True)
    pub.publish(utterance)
    
    console_log('say : "' + utterance + '"')

    time.sleep(duration_utterance)
    console_log('speech is done')

# ---------------------------- loop of actions -------------------------------
# ----------------------------------------------------------------------------

# main cycle : detect user angle -> rotate -> detect user distance -> move forward 
#              -> dialog -> move_backward -> rotate to initial position -> ...
def main_action_loop():
    console_log(' ---------- begins main action loop -------- ')
    
    # detect user angle
    audio_source_angle = wait_new_value_of_local_topic('audio_source_angle')
    # rotation 
    move(angle_degree = audio_source_angle)
    
    # ----- detect user distance -----
    distance_obstacle = wait_new_value_of_local_topic('distance_obstacle')
    # distance to travel
    distance_travel = distance_obstacle - DISTANCE_TO_USER_DURGING_DIALOG
    if distance_travel < 0: distance_travel = 0
    console_log('to meet the user, we move forward of ' + str(distance_travel) + " m")

    # go forward
    move(x=distance_travel)
    # dialog
    dialog_loop()
    # go backward 
    move(x = -distance_travel)
    # rotation 
    move(angle_degree = -audio_source_angle)

    console_log(' ---------- main action loop is done -------- ')

# dialog : 'can I help you ?' -> LOOP[ user_utterance -> nndial -> system_response ]
def dialog_loop():
    console_log(' ----- dialog begins ------')
    speak('Hello ! How can I help you ?')

    # ----- nndial dialog -----

    # dialog state initialization
    nndial_dialog_state = { "generated": "", "venue_offered": {}, "selected_venue": -1, "belief_t": [] } # note : add 'user_utt_t' to request nndial
    user_utterance = pepper_utterance = ''

    # The dialog stops when the user or pepper says 'goodbye' or pepper says 'thank you'
    while not contains(user_utterance, 'goodbye') \
        and not contains(pepper_utterance, 'goodbye') \
        and not contains(pepper_utterance, 'thank you'):

        user_utterance = wait_new_value_of_local_topic('utterance_heard')
        
        # create request
        nndial_request = nndial_dialog_state
        nndial_request['user_utt_t'] = user_utterance
        # we update the dialog state with nndial response
        nndial_dialog_state = request_nndial(nndial_request)
        
        # pepper says the answer
        pepper_utterance = nndial_dialog_state['generated'][5:-5]
        speak(pepper_utterance)

    console_log(' ----- dialog is done -----')

if __name__ == "__main__":

    # rosnode initialization
    rospy.init_node('pepper_restaurant_agent', anonymous=True)
    
    # we call the trigger functions on new topics values
    rospy.Subscriber('/nao_audio/audio_source_localization', AudioSourceLocalization, on_new_audio_source_localization)
    rospy.Subscriber('/commands_text', String, on_new_utterance_heard)
    rospy.Subscriber('/pepper_robot/naoqi_driver/sonar/front', Range, on_new_sonar_distance)

    while True:
        main_action_loop()