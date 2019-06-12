import json
import rospy
import requests
import speech.speech_config as speech_cfg

from std_msgs.msg import String


class NaturalLanguageProcessor:
	def __init__(self):
		self.speech_subscriber = rospy.Subscriber('/commands_text', String, self.on_text_received)
		self.commands_publisher = rospy.Publisher('/commands_structured', String, queue_size=10)

	def on_text_received(self, received_data):
		data = json.loads(received_data.data)
		if not data['text']:
			return
		response = self.call_wit(data['text'].strip().lower(), data['language'])
		if not response:
			return
		interpreted_speech = self.interpret(response)
		if not interpreted_speech:
			return
		self.commands_publisher.publish(json.dumps(interpreted_speech))

	def call_wit(self, text, language='en-EN'):
		if not text:
			return None

		params = {'access_token': speech_cfg.access_keys[language], 'q': text}
		response = requests.get(url=speech_cfg.URL, params=params).json()
		return response

	def interpret(self, response):
		# The response should contain entities associated with the query.
		if 'entities' not in response:
			print('API server error: ' + str(response))
			return None

		# Check that entities contain an intent.
		entities = response['entities']
		if 'intent' not in entities or len(entities['intent']) == 0:
			print('No intent found.')
			return None
		intent = entities['intent'][0]

		# Check that we have the mandatory entities to create a task.
		if not self.check_mandatory_entities(speech_cfg.mandatory_intent_entities[intent['value']], entities):
			print('Missing required entity.')
			return None

		mandatory_entities = self.get_mandatory_entities(speech_cfg.mandatory_intent_entities[intent['value']], entities)
		optional_entities = self.get_optional_entities(speech_cfg.mandatory_intent_entities[intent['value']], entities)

		interpreted_speech = {
			'intent': intent['value'],
			'mandatory_entities': mandatory_entities,
			'optional_entities': optional_entities
		}
		self.print_interpreted_speech(interpreted_speech)
		return interpreted_speech

	def print_interpreted_speech(self, interpreted_speech):
		print('\nInterpreted speech:')
		print('\tIntent: ' + str(interpreted_speech['intent'].upper()))
		print('\tEntities - mandatory: ' + str(interpreted_speech['mandatory_entities']))
		print('\t            optional: ' + str(interpreted_speech['optional_entities']))

	def check_mandatory_entities(self, mandatory_entities, received_entities):
		for entity in mandatory_entities:
			if entity not in received_entities:
				return False
		return True

	def get_mandatory_entities(self, mandatory_entities, received_entities):
		entities = {}
		for mandatory_entity in mandatory_entities:
			for received_entity in received_entities[mandatory_entity]:
				entities[mandatory_entity] = received_entity['value']
		return entities

	def get_optional_entities(self, mandatory_entities, received_entities):
		entities = {}
		for received_entity in received_entities.keys():
			if received_entity not in mandatory_entities and received_entity != 'intent':
				for entity in received_entities[received_entity]:
					entities[received_entity] = entity['value']
		return entities


if __name__ == '__main__':
	NaturalLanguageProcessor()