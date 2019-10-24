
from devices.light import MagicHomeLight
from devices.scene import MagicHomeScene
from devices.switch import MagicHomeSwitch
from devices.socket import MagicHomeSocket
from devices.controller import MagicHomeController

def get_magichome_device(data, api):

    print("Factory data:",data)
    print("Factory api: ",api)
    dev_type = data.get('deviceType')
    devices = []

    if dev_type == 'light':
        devices.append(MagicHomeLight(data, api));
    elif dev_type == 'scene':
        devices.append(MagicHomeScene(data, api));
    elif dev_type == 'switch':
        devices.append(MagicHomeSwitch(data, api));
    elif dev_type == 'socket':
        devices.append(MagicHomeSocket(data, api));
    elif dev_type == 'controller':
        devices.append(MagicHomeController(data, api));

    return devices

