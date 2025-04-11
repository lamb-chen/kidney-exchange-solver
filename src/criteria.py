class MaxTwoCycles():
    def __init__(self):
        self.obj = "MAX"

    def cycle_val(self, cycle):
        if cycle.length == 2:
            return 1
        return 0

    def altruist_val(self):
        return 0

class MaxSize():
    def __init__(self):
        self.obj = "MAX"

    def cycle_val(self, cycle): 
        return cycle.length

    def altruist_val(self):
        return 0
    
class MinThreeCycles():
    def __init__(self):
        self.obj = "MIN"

    def cycle_val(self, cycle): 
        return cycle.length == 3

    def altruist_val(self):
        return 0


class MaxBackarcs():
    def __init__(self):
        self.obj = "MAX"
        
    def cycle_val(self, cycle): 
        if cycle.length < 3:
            return 0
        return cycle.find_num_of_backarcs()

    def altruist_val(self):
        return 1
    
class MaxOverallWeight():
    def __init__(self):
        self.obj = "MAX"
        
    def cycle_val(self, cycle): 
        return cycle.get_cycle_weight()

    def altruist_val(self):
        return 0