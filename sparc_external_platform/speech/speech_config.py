from speech.subject_presentations import *
from utils.utils import *

# Wit.ai api params.
URL = 'https://api.wit.ai/message'
access_keys = {'en-EN':  'VAYDJDTZRU4644WDEK4Q6YVXLY47F7GC', 'ro-RO': 'AOWWWDRYJW6C3MODYRQKJY25YSCNBLFD'}

# Wit.ai intent-entity association.
SAY_INTENT = 'say'
SEARCH_INTENT = 'look'
GO_TO_INTENT = 'go to'
FIND_INTENT = 'find'
STOP_INTENT = 'stop'
HELLO_INTENT = 'hello'
REMINDERS_INTENT = 'reminders'
NEXT_INTENT = 'next'
PREVIOUS_INTENT = 'previous'
HEALTH_INTENT = 'health'
ACTUATION_INTENT = 'actuate'
REMEMBER_INTENT = 'remember'

mandatory_intent_entities = {
	SAY_INTENT: ['target'],
	SEARCH_INTENT: ['target'],
	GO_TO_INTENT: ['target'],
	FIND_INTENT: ['target'],
	REMINDERS_INTENT: ['target'],
	NEXT_INTENT: [],
	PREVIOUS_INTENT: [],
	HEALTH_INTENT: ['health_entity'],
	STOP_INTENT: [],
	ACTUATION_INTENT: ['target'],
	REMEMBER_INTENT: [],
	HELLO_INTENT: []
}

# Association between subjects and presentations.
presentations = {'lab308': lab308_presentation,
				'lab303': lab303_presentation,
				'lab306': lab306_presentation,
				'home': robot_presentation,
				'alex': alex_presentation,
				'stephanie': stephanie_presentation,
				'time': get_time_presentation,
				'weather': get_weather_report,
				'default': default_presentation}

# Response for Hello intent
hello_response = 'hello'

# Eyes fade duration.
fade_duration = 1.0

# Time to wait in listen task for an answer.
time_to_listen = 7