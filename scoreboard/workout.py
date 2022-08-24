
import json


def exercise_sort(ex):
    return ex['position']


class Workout:
    def __init__(self, data):
        self.workout = json.loads(data)
        self.workout['exercises'].sort(key=exercise_sort)
        self.exercise_idx = None
        self.current_set = 0
        self.duration = 0
        self.paused = False
        self.resting = False


    def name(self):
        try:
            return self.workout['name']
        except:
            return None


    def in_progress(self):
        return self.current_exercise() != None


    def start(self):
        self.exercise_idx = -1
        self.next_exercise()


    def pause(self):
        self.paused = not self.paused


    def tick(self):
        if self.paused: return
        if self.resting:
            if self.exercise_rest() < 0: return
            self.duration += 1
            if self.duration > self.exercise_rest():
                self.next_set()
        else:
            if self.exercise_type() == 'repetitions': return
            self.duration += 1
            if self.duration > self.exercise_target():
                self.finish_set()


    def time_remaining(self):
        if self.resting: return self.exercise_rest() - self.duration
        return self.exercise_target() - self.duration


    def current_exercise(self):
        try:
            return self.workout['exercises'][self.exercise_idx]
        except:
            return None


    def next_exercise(self):
        try:
            self.exercise_idx += 1
            self.current_set = 1
            self.paused = self.current_exercise()['pause']
        except:
            self.exercise_idx = None


    def previous_exercise(self):
        if self.exercise_idx > 0:
            self.exercise_idx -= 1
            self.current_set = self.exercise_sets()
            self.paused = self.current_exercise()['pause']


    def exercise_name(self):
        try:
            return self.current_exercise()['name']
        except:
            return None


    def exercise_sets(self):
        try:
            return int(self.current_exercise()['sets'])
        except:
            return 0


    def next_set(self):
        self.current_set += 1
        self.resting = False
        self.duration = 0
        if self.current_set > self.exercise_sets():
            self.next_exercise()
        else:
            self.paused = self.current_exercise()['pause']


    def finish_set(self):
        if self.exercise_rest() == 0:
            self.next_set()
        else:
            self.resting = True
            self.duration = 0


    def previous_set(self):
        self.resting = False
        self.duration = 0
        if self.current_set < 2:
            self.previous_exercise()
        else:
            self.current_set -= 1


    def exercise_type(self):
        try:
            return self.current_exercise()['exercise_type']
        except:
            return None


    def exercise_target(self):
        try:
            target = self.current_exercise()['target'].split('/')
            if len(target) >= self.current_set: return int(target[self.current_set - 1])
            return int(target[-1])
        except:
            return 0


    def exercise_rest(self):
        try:
            rest = self.current_exercise()['rest'].split('/')
            if len(rest) >= self.current_set: return int(rest[self.current_set - 1])
            return int(rest[-1])
        except:
            return 0


    def exercise_notes(self):
        try:
            return self.current_exercise()['notes']
        except:
            return ""
