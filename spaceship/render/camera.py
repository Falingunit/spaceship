from ..render.entity import Entity
from ..utils.math import Vector
from ..utils.constants import SIZE_X, SIZE_Y

from enum import Enum
class CameraMode(Enum):
    CENTER = 0
    TOP_LEFT = 1
    TOP_RIGHT = 2
    BOT_LEFT = 3
    BOT_RIGHT = 4

class Camera:
    def __init__(self, position: Vector = Vector(), cameraMode: CameraMode = CameraMode.CENTER):
        self.position = position
        self.mode = cameraMode
        self.size = Vector(SIZE_X, SIZE_Y)

    def get_transformed_vector(self, vector):
        
        offset = Vector((float)((int)(SIZE_X / 2)), (float)((int)(SIZE_Y / 2)))
        if self.mode == CameraMode.TOP_LEFT:
            offset = Vector()
        elif self.mode == CameraMode.TOP_RIGHT:
            offset = Vector(SIZE_X - 1, 0)
        elif self.mode == CameraMode.BOT_LEFT:
            offset = Vector(0, SIZE_Y - 1)
        elif self.mode == CameraMode.BOT_RIGHT:
            offset = Vector(SIZE_X - 1, SIZE_Y - 1)

        return vector - self.position + offset
    
    def get_render(self, display_size: Vector, entities: list[Entity]) -> list[str]:
        
        render = [{'display': ' ', 'priority': 0}] * (int)(display_size.x * display_size.y)

        for entity in entities:
            sprite = entity.render()
            center_position_wrt_camera = self.get_transformed_vector(sprite.position)

            for y, line in enumerate(sprite.decoded_string):
                for x, pixel in enumerate(line):

                    pixel_position_wrt_center = Vector(x, y) - sprite.center
                    pixel_position_wrt_camera = pixel_position_wrt_center + center_position_wrt_camera

                    if 0 > pixel_position_wrt_camera.x or pixel_position_wrt_camera.x >= display_size.x or 0 > pixel_position_wrt_camera.y or pixel_position_wrt_camera.y >= display_size.y:
                        continue

                    pixel_index = get_index(pixel_position_wrt_camera, display_size)
                    if sprite.priority >= render[pixel_index]['priority']:
                        render[pixel_index] = {'display': pixel, 'priority': sprite.priority}

        # Convert into string grid         
        render_grid = [' '] * len(render)
        for i, pixel in enumerate(render):
            render_grid[i] = pixel['display']
        return render_grid

def get_index(position: Vector, size: Vector) -> int:
    return (int)(position.x + position.y * size.x)