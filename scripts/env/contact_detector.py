from humanoid_robot.msg import Contacts

class ContactDetector:
    def __init__(self, env):
        self.env = env
        self.game_over = False
        self.enable_detection = False
        self.left_foot_contact = False
        self.right_foot_contact = False

        self.subscription = self.env.create_subscription(Contacts, '/contacts', self._callback, 10)

    def _callback(self, msg):
        for contact in msg.states:
            if "base_link" in contact.info and "ground_plane" in contact.info:
                if self.enable_detection:
                    self.game_over = True
                    break

            if self.enable_detection:
                if "left_foot" in contact.info and "ground_plane" in contact.info:
                    self.left_foot_contact = True
                if "right_foot" in contact.info and "ground_plane" in contact.info:
                    self.right_foot_contact = True
    

    def has_fallen(self):
        return self.game_over
    
    def foot_contact(self):
        return self.left_foot_contact, self.right_foot_contact
    
    def set_enable_detection(self, enable):
        self.enable_detection = enable
    
    def reset_foot_contact(self):
        self.left_foot_contact = False
        self.right_foot_contact = False

    def reset(self):
        self.game_over = False
        self.enable_detection = False