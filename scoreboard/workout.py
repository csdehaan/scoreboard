

class Workout:
    def __init__(self, data):
        self.workout = data
        self.current_exercise = None
        self.current_set = 0


    def name(self):
        try:
            return self.workout['name']
        except:
            return None


    def in_progress(self):
        return self.current_exercise != None


    def start(self):
        self.next_exercise()


    def next_exercise(self):
        try:
            self.current_exercise = self.workout['exercises'].pop(0)
            self.current_set = 1
        except:
            self.current_exercise = None


    def exercise_name(self):
        try:
            return self.current_exercise['name']
        except:
            return None


    def exercise_sets(self):
        try:
            return int(self.current_exercise['sets'])
        except:
            return 0


    def next_set(self):
        self.current_set += 1
        if self.current_set > self.exercise_sets():
            self.next_exercise()


    def exercise_target(self):
        try:
            return self.current_exercise['name']
        except:
            return None


    def exercise_notes(self):
        try:
            return self.current_exercise['notes']
        except:
            return ""
