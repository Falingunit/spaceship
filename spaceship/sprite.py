
class Sprite:
    """Depicts an ASCII sprite"""

    def __init__(self):
        
        self.raw_string = ''
        self.decoded_string = []
        self.size_x = 0
        self.size_y = 0
        self.center_x = 0
        self.center_y = 0
        self.priority = 1

        self.position_x = 0
        self.position_y = 0
    
    def set_position(self, x, y):
        self.position_x = x
        self.position_y = y

    def load(self, raw_string, priority = 1):
        
        lines = raw_string.split('\n')

        center_x = -1
        center_y = -1
        for i, line in enumerate(lines):
            
            if '\t' in line:
                center_x = line.index('\t')
                center_y = i
                
                lines[i] = line[:center_x] + line[center_x + 1:]
        
        if center_x == center_y == -1:
            raise ValueError("No center defined")
        
        #Store values
        self.raw_string = raw_string
        self.decoded_string = lines
        self.center_x = center_x
        self.center_y = center_y
        self.size_x = len(lines[0])
        self.size_y = len(lines)
        self.priority = 1