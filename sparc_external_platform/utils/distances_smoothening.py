import numpy as np
import collections

from matplotlib import pyplot as plt
from pykalman import KalmanFilter

# class KalmanSmoother(object):
#	 def __init__(self, initial_position):
#		 self.process_variance = 1e-5
#		 self.estimated_measurement_variance = 0.3
#		 self.posteri_estimate = initial_position
#		 self.posteri_error_estimate = 0.3

#		 self.last3_measurements = collections.deque(maxlen=5)

#	 def get_distance_estimation(self, measurement):
#	 	self.last3_measurements.append(measurement)
#	 	data = np.median(self.last3_measurements)

#		 priori_estimate = self.posteri_estimate
#		 priori_error_estimate = self.posteri_error_estimate + self.process_variance

#		 blending_factor = priori_error_estimate / (priori_error_estimate + self.estimated_measurement_variance)
#		 self.posteri_estimate = priori_estimate + blending_factor * (data - priori_estimate)
#		 self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

#	 	return self.posteri_estimate

# class KalmanSmoother(object):
# 	def __init__(self, initial_position):
# 		# self.process_variance = 1e-5
# 		# self.estimated_measurement_variance = 0.3
# 		# self.posteri_estimate = initial_position
# 		# self.posteri_error_estimate = 0.3

# 		# self.last3_measurements = collections.deque(maxlen=5)
# 		self.last_measurements = collections.deque(maxlen=10)
# 		self.corrected_measurements = collections.deque(maxlen=10)
# 		self.kf = KalmanFilter(initial_state_mean=0, n_dim_obs=1)

# 	def get_distance_estimation(self, measurement):
# 		self.last_measurements.append(measurement)
# 		if len(self.last_measurements) < 5:
# 			self.corrected_measurements.append(measurement)
# 			return None



# 		smoothened_distances = self.kf.smooth(self.last_measurements)[0]
# 		self.corrected_measurements.append(smoothened_distances[-1])
# 		return smoothened_distances[-1]

class KalmanSmoother:
	def __init__(self, orice):
		self.kf = KalmanFilter(transition_matrices=np.matrix('''
		    1. 0.;
			0. 1.
		'''), observation_matrices=np.matrix('''
			1. 0.;
			0. 1.
		'''))
		self.filtered_state_means = np.zeros((2))
		self.filtered_state_covariances = np.matrix(np.eye(2))*1000

	def get_distance_estimation(self, observation):
		self.filtered_state_means, self.filtered_state_covariances = self.kf.filter_update(self.filtered_state_means, self.filtered_state_covariances, observation)
		return self.filtered_state_means[0]
		


if __name__ == '__main__':
	distances = [2.8696470588235292, 1.8406274509803922, 1.8277647058823527, 
				1.8277647058823527, 1.8277647058823527, 1.8277647058823527, 
				1.8534901960784311, 1.8277647058823527, 3.0754509803921564, 
				1.5061960784313726, 1.4290196078431374, 2.2007843137254901, 
				1.5962352941176468, 1.6219607843137256, 1.5705098039215688, 
				1.351843137254902, 2.1107450980392155, 1.54478431372549, 
				1.5576470588235294, 1.4547450980392158, 1.4290196078431374, 
				1.3904313725490196, 1.4547450980392158, 1.3904313725490196, 
				2.2393725490196079, 1.4676078431372548, 1.3775686274509802, 
				1.300392156862745, 1.3904313725490196, 1.3775686274509802, 
				1.3261176470588234, 1.2746666666666666, 2.0464313725490193, 
				1.2103529411764706, 1.2489411764705882, 1.184627450980392, 
				1.0302745098039217, 1.0817254901960784, 1.171764705882353, 
				1.068862745098039, 2.1107450980392155, 1.120313725490196, 
				1.0045490196078433, 0.94023529411764706, 1.0431372549019606, 
				1.0045490196078433, 1.0045490196078433, 0.99168627450980396, 
				0.97882352941176476, 0.97882352941176476, 0.97882352941176476, 
				0.96596078431372545, 0.95309803921568625, 0.95309803921568625, 
				0.95309803921568625, 0.95309803921568625, 0.91450980392156866, 
				0.97882352941176476, 0.92737254901960786, 0.96596078431372545,
				0.94023529411764706, 0.91450980392156866, 0.85019607843137257, 
				0.81160784313725487, 0.88878431372549016, 0.87592156862745107, 
				0.87592156862745107, 0.83733333333333326, 0.85019607843137257, 
				0.85019607843137257, 0.81160784313725487, 0.79874509803921567, 
				0.82447058823529418, 0.82447058823529418, 0.78588235294117648, 
				0.78588235294117648, 0.79874509803921567, 0.81160784313725487, 
				0.83733333333333326, 0.82447058823529418, 0.83733333333333326, 
				1.5833725490196078]

	plt.title('Distances')
	plt.plot(np.linspace(1, len(distances), len(distances)), distances)

	smoothened_distances = []
	kalman_filter = KalmanSmoother(distances[0])

	for iteration in range(1, len(distances)):
		smoothened_distances.append(kalman_filter.get_distance_estimation(distances[iteration]))

	plt.title('Estimation')
	plt.plot(np.linspace(1, len(smoothened_distances), len(smoothened_distances)), smoothened_distances)

	plt.show()