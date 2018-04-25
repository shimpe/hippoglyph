from myimage import MyImage

class MyModel(object):
    def __init__(self):
        self.model_elements = {
            'crosspoints': [],
            'triggers': []
        }
        self.total_time = 0
        self.time_left = 0
        self.camera_image = None

    def set_camera_image(self, scene, camera_image):
        if scene is not None and camera_image is not None:
            if self.camera_image is not None:
                self.camera_image.remove_from_scene(scene)
            self.camera_image = MyImage(camera_image)
            self.camera_image.add_to_scene(scene, -500, -500, 500 * 2, 500 * 2)
