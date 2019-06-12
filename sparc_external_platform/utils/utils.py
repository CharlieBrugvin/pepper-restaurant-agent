from calendar import TimeEncoding, month_name
from datetime import datetime
from dateutil import parser
from weather import Weather, Unit


# Auxiliary structure for 'time' subject.
class Dict(dict):
	def __getitem__(self, key):
		val = super(Dict, self).__getitem__(key)
		if callable(val):
			return val()
		return val


def get_weather_report(optional_parameters):
	if not 'datetime' in optional_parameters:
		return "Sorry, I don't know"
	date = parser.parse(optional_parameters['datetime'])
	weather = Weather(unit=Unit.CELSIUS)
	location = weather.lookup_by_location('bucharest')
	forecasts = location.forecast
	for forecast in forecasts:
		dt = parser.parse(forecast.date)
		if dt.day == date.day and dt.month == date.month and dt.year == date.year:
			with TimeEncoding("en_US.UTF-8") as encoding:
				month = month_name[date.month]
			return 'On %s %s it will be %s. The maximum temperature is %s degrees celsius' % (date.day, month, forecast.text, forecast.high)


def get_time_presentation(optional_parameters):
	time = datetime.now()
	return 'It is ' + str(time.hour) + ' ' + str(time.minute)
