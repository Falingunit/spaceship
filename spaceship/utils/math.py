import math

class Vector:  
    def __init__(self, x: float = 0, y: float = 0):
        self._x = x
        self._y = y

    @property
    def x(self): return self._x
    @x.setter
    def x(self, new_x): self._x = new_x
    
    @property
    def y(self): return self._y
    @y.setter
    def y(self, new_y): self._y = new_y
    
    def length(self):
        return math.sqrt(self.length_squared())
    
    def length_squared(self):
        return self.x**2 + self.y**2
    
    def dot(self, other):
        return Vector(self.x * other.x, self.y * other.y)

    def cross(self, other):
        return self.x * other.y - self.y * other.x

    def scale(self, factor):
        return Vector(self.x * factor, self.y * factor)

    # Operations
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Vector(-self.x, -self.y)
    
    # Scalar-product or Dot-product
    def __mul__(self, other):
        if isinstance(other, float):
            return self.scale(other)
        elif isinstance(other, Vector):
            return self.dot(other)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)
    
    # Magnitude of cross-product
    def __matmul__(self, other):
        return self.cross(other)
    
    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return False

    def __str__(self) -> str:
        return f"X:{self.x} Y:{self.y}"
    
    def __repr__(self) -> str:
        return f"X:{self.x} Y:{self.y}"
