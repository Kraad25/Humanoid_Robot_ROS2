from humanoid_robot.msg import Contacts

class ContactDetector:
    def __init__(self, env):
        self.env = env
        self.game_over = False
        self.enable_detection = False

        self.find_contacts = self.env.create_subscription(Contacts ,"/contacts", self._callback, 10)

    def _callback(self, msg):
        if not self.enable_detection:
            return
        
        for contact in msg.states:
            if "foot_right" in contact.info and "ground_plane" in contact.info:
                self.env.right_foot_contact = True
                continue

            if "foot_left" in contact.info and "ground_plane" in contact.info:
                self.env.left_foot_contact = True
                continue
            
            if "ground_plane" in contact.info:
                self.game_over = True
                break
    
    def set_enable_detection(self, enable):
        self.enable_detection = enable

    def has_fallen(self):
        return self.game_over
    
    def reset(self):
        self.game_over = False
        self.enable_detection = False