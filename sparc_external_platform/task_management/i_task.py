from enum import Enum


class TaskStatus(Enum):
	PENDING = 1
	RUNNING = 2
	FINISHED = 3
	FAILED = 4
	STOPPED = 5


class ITask:
	def __init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority):
		self.run_method = run_method
		self.stop_method = stop_method
		self.success_child = success_child
		self.fail_child = fail_child
		self.add_to_queue_method = add_to_queue_method
		self.priority = priority
		self.status = TaskStatus.PENDING

	def run(self):
		self.status = TaskStatus.RUNNING
		if self.run_method:
			self.run_method(self.on_success, self.on_fail)

	def on_success(self, select_child=None):
		self.status = TaskStatus.FINISHED
		success_child = self.success_child
		if select_child and self.success_child:
			success_child = self.success_child[select_child]
		if success_child:
			self.add_to_queue_method(success_child)

	def on_fail(self):
		self.status = TaskStatus.FAILED
		if self.fail_child:
			self.add_to_queue_method(self.fail_child)

	def stop(self):
		if self.stop_method:
			self.stop_method()
		self.status = TaskStatus.STOPPED

	def stringify(self):
		return 'Generic task'

	def __str__(self):
		return self.stringify()

	def __repr__(self):
		return self.__str__()
