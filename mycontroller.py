from pythonosc import udp_client

SUPERCOLLIDER_PORT = 57120
GODOT_PORT = 23000

class MyController(object):
    def __init__(self, datamodel, verbose=True):
        self.verbose = verbose
        try:
            self.supercollider = udp_client.SimpleUDPClient("127.0.0.1", SUPERCOLLIDER_PORT)
        except Exception as e:
            print("Exception occurred:\n{0}".format(e))
            self.supercollider = None
        try:
            self.godot = udp_client.SimpleUDPClient("127.0.0.1", GODOT_PORT)
        except Exception as e:
            print("Exception occurred:\n{0}".format(e))
            self.godot = None
        self.datamodel = datamodel

    def send_updates(self):
        for w in self.datamodel.words:
            if self.verbose:
                print("/camera/word ", w[1], w[2], w[0][0])
            self.supercollider.send_message("/camera/word", [w[1], w[2], w[0][0]])
