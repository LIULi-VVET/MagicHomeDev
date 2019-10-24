import time


class MagicHomeDevice(object):


    def __init__(self, data, api):
        self.api = api
        self.data = data.get('properties')
        self.obj_id = data.get('deviceId')
        self.obj_type = data.get('ha_type')
        self.obj_name = data.get('deviceName')
        self.dev_type = data.get('deviceType')
        self.icon = data.get('icon')
        print("init data",self.data)
        print("init obj_id",self.obj_id)
        print("init obj_type",self.obj_type)
        print("init obj_name",self.obj_name)
        print("init dev_type",self.dev_type)
        print("init icon",self.icon)

    def name(self):
        return self.obj_name

    def state(self):
        state = self.data.get('state')
        if state == 'true':
            return True
        else:
            return False

    def device_type(self):
        return self.dev_type

    def object_id(self):
        return self.obj_id

    def object_type(self):
        return self.obj_type

    def available(self):
        return self.data.get('online')

    def iconurl(self):
        return self.icon

    def update(self):
        """Avoid get cache value after control."""
        time.sleep(0.5)
        success, response = self.api.device_control(
            self.obj_id, 'Query', namespace='query')
        if success:
            self.data = response['payload']['data']
            return True
        return
        
