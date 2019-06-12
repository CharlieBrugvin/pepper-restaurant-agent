from task_management.i_task import ITask, TaskStatus

import tasks_config as cfg


class SayTask(ITask):
    def __init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority, text):
        ITask.__init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority)
        self.text = text

    def run(self):
        self.status = TaskStatus.RUNNING
        if callable(self.text):
            self.text = self.text()
        self.run_method(self.text, self.on_success, self.on_fail)

    def stringify(self):
        return '%16s: Prior=%d Status=%-20s Target=%s' % \
               (self.__class__.__name__, self.priority, str(self.status),
                str(self.text) if len(str(self.text)) < cfg.max_display_length else str(self.text)[:(cfg.max_display_length-3)] + '...')


class ListenTask(ITask):
    def __init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority, keywords):
        ITask.__init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority)
        self.keywords = keywords
        self.result = None

    def save_result(self, text):
        self.result = text

    def get_result(self):
        return self.result

    def run(self):
        self.status = TaskStatus.RUNNING
        self.run_method(self.keywords, self.save_result, self.on_success, self.on_fail)

    def stringify(self):
        return '%16s: Prior=%d Status=%-20s Target=%s' % \
               (self.__class__.__name__, self.priority, str(self.status), self.keywords)


class MoveToTask(ITask):
    def __init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority, target):
        ITask.__init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority)
        self.target = target

    def run(self):
        self.status = TaskStatus.RUNNING
        self.run_method(self.target, self.on_success, self.on_fail)

    def stringify(self):
        if self.target:
            position = self.target.pose.position
            position = '(%.2f %.2f %.2f)' % (position.x, position.y, position.z)
        else:
            position = 'none'
        return '%16s: Prior=%d Status=%-20s Target=%s' % \
               (self.__class__.__name__, self.priority, str(self.status), position)


class SearchTargetTask(ITask):
    def __init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority, target):
        ITask.__init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority)
        self.target = target

    def run(self):
        self.status = TaskStatus.RUNNING
        self.run_method(self.target, self.on_success, self.on_fail)

    def stringify(self):
        return '%16s: Prior=%d Status=%-20s Target=%s' % \
               (self.__class__.__name__, self.priority, str(self.status), self.target)


class ShowURLTask(ITask):
    def __init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority, url):
        ITask.__init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority)
        self.url = url

    def run(self):
        self.status = TaskStatus.RUNNING
        self.run_method(self.url, self.on_success, self.on_fail)

    def stringify(self):
        return '%16s: Prior=%d Status=%-20s Target=%s' % \
               (self.__class__.__name__, self.priority, str(self.status),
                self.url if len(self.url) < cfg.max_display_length else self.url[:(cfg.max_display_length-3)] + '...')


class ActuationTask(ITask):
    def __init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority, target, optional_entities=None):
        ITask.__init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority)
        self.target = target
        self.optional_entities = optional_entities

    def run(self):
        self.status = TaskStatus.RUNNING
        self.run_method(self.target, self.optional_entities, self.on_success, self.on_fail)

    def stringify(self):
        return '%16s: Prior=%d Status=%-20s Target=%s Optional=%s' % \
               (self.__class__.__name__, self.priority, str(self.status), self.target, self.optional_entities)


class RememberTargetTask(ITask):
    def __init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority, target, target_type):
        ITask.__init__(self, run_method, stop_method, success_child, fail_child, add_to_queue_method, priority)
        self.target = target
        self.target_type = target_type

    def run(self):
        self.status = TaskStatus.RUNNING
        if callable(self.target):
            self.target = self.target()
        self.run_method(self.target, self.target_type, self.on_success, self.on_fail)

    def stringify(self):
        return '%16s: Prior=%d Status=%-20s Target=%s Target_type=%s' % \
               (self.__class__.__name__, self.priority, str(self.status), str(self.target), self.target_type)

