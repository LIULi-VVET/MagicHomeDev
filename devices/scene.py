from devices.base import MagicHomeDevice

class MagicHomeScene(MagicHomeDevice):

    def avaliable(self):
        return True
        
        
    def activate(self):
        self.api.device_control(self.obj_id,'TurnOn',{'value':'1'})
        

    def update(self):
        return True