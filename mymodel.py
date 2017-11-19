from crosspoint import CrossPoint
from myimage import MyImage
from trigger import GreenTrigger, RedTrigger, YellowTrigger
from constants import MERGEDISTANCE
from utils import distance


class MyModel(object):
    def __init__(self, udp_client):
        self.model_elements = {
            'crosspoints': [],
            'triggers': []
        }
        self.total_time = 0
        self.time_left = 0
        self.camera_image = None
        self.udp_client = udp_client

    def clear_crosspoints(self):
        self.model_elements['crosspoints'] = []

    def clear_triggers(self):
        self.model_elements['triggers'] = []

    def add_crosspoint(self, x, y, label, rays, color):
        self.model_elements['crosspoints'].append(CrossPoint(x, y, label, rays, color))

    def update_crosspoint(self, x, y, label, rays, color):
        for el in self.model_elements['crosspoints']:
            if distance(x, y, el.x, el.y) < MERGEDISTANCE:
                el.set_visited(True)
                return
        self.add_crosspoint(x, y, label, rays, color)

    def add_trigger(self, x, y, color):
        self.model_elements['triggers'].append(YellowTrigger(x, y, color))

    def update_trigger(self, x, y, color):
        for el in self.model_elements['triggers']:
            if distance(x, y, el.x, el.y) < MERGEDISTANCE:
                el.set_visited(True)
                return
        self.add_trigger(x, y, color)

    def add_to_scene(self, scene, minx, miny, maxx, maxy):
        for group in self.model_elements:
            for el in self.model_elements[group]:
                if not el.added:
                    el.add_to_scene(scene, minx, miny, maxx, maxy)

    def prepare_update(self):
        for group in self.model_elements:
            for el in self.model_elements[group]:
                el.set_visited(False)

    def finish_update(self):
        for key in self.model_elements:
            for_removal = [el for el in self.model_elements[key] if not el.visited]
            for_keep = [el for el in self.model_elements[key] if el.visited]
            for el in for_removal:
                el.remove_from_scene()
            self.model_elements[key] = for_keep

    def update(self, deltat):
        for el in self.model_elements['crosspoints']:
            collides = False
            collisionInfo = {}
            for t in self.model_elements['triggers']:
                if el.collidesWithItem(t):
                    collides = True
                    collisionInfo.update(t.get_collision_info())
            el.update(self.udp_client, deltat, collides, collisionInfo)

        for el in self.model_elements['triggers']:
            el.update(self.udp_client, deltat, collisionInfo)

    def update_time_left(self, total_time, time_left):
        self.total_time = total_time
        self.time_left = time_left

    def set_camera_image(self, scene, camera_image):
        if scene is not None and camera_image is not None:
            if self.camera_image is not None:
                self.camera_image.remove_from_scene(scene)
            self.camera_image = MyImage(camera_image)
            self.camera_image.add_to_scene(scene, -500, -500, 500 * 2, 500 * 2)
