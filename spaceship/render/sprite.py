
from ..utils.math import Vector

class Sprite:
    """Depicts an ASCII sprite"""

    def __init__(self):
        
        self.raw_string = ''
        self.decoded_string = []
        self.size = Vector()
        self.center = Vector()
        self.priority = 1

        self.position = Vector()

    def load(self, raw_string, priority = 1):
        
        lines = raw_string.split('\n')

        centerDefined = False
        for i, line in enumerate(lines):
            
            if '\t' in line:
                centerDefined = True
                self.center = Vector(line.index('\t'), i)
                lines[i] = line[:self.center.x] + line[self.center.x + 1:]
        
        if centerDefined == False:
            self.center = Vector()
        
        #Store values
        self.raw_string = raw_string
        self.decoded_string = lines
        self.size = Vector(len(lines[0]), len(lines))
        self.priority = priority