import json
import logging
import requests
import time
import hashlib
import uuid

from devices.factory import get_magichome_device
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Certification is not provided
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

MAGHCHOMECLOUDURL = "https://wifij01{}.magichue.net"
DEFAULTREGION = 'us'

REFRESHTIME = 60 * 60 * 12

_LOGGER = logging.getLogger(__name__)


class MagicHomeSession:

    username = ''
    password = ''
    countryCode = ''
    bizType = ''
    accessToken = ''
    refreshToken = ''
    expireTime = 0
    devices = []
    region = DEFAULTREGION

SESSION = MagicHomeSession()


class MagicHomeApi:



    # this userName password countryCode bizType
    def init(self, username, password, countryCode, bizType=''):
        SESSION.username = username
        SESSION.password = self.md5(password)
        SESSION.countryCode = countryCode
        SESSION.bizType = bizType
        
        # Return None if username is None or password is None
        # Otherwise try to get the token
        
        if username is None or password is None:
            return None
        else:
            self.get_access_token()
            self.discover_devices(self)
            # print(json.dumps(SESSION.devices))
            return SESSION.devices
            
            
            
    def get_access_token():
        headers = {
            'Content-Type': 'application/json;charset=UTF-8;'
        }
        response = requests.post(
            (MAGHCHOMECLOUDURL+'/authorizationCode/ZG001').format(SESSION.region),
            headers=headers,
            data = json.dumps({
                "username": SESSION.username,
                "password": SESSION.password,
                "cdpid": "ZG001",
                "client_id": "py_Api",
                "response_type": "",
                "state": "state",
                "redirect_uri": "redirect_uri"
            }),
            verify=False
        )
        response_json = response.json()

        if response_json.get('responseStatus') == 'error':
            message = response_json.get('msg')
            if message == 'error':
                raise MagicHomeApiException("get access token failed")
            else:
                raise MagicHomeApiException(message)

        code = response_json.get("code");
        
        responsetk = requests.post(
            (MAGHCHOMECLOUDURL+'/authorizationToken').format(SESSION.region),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data = {
                "client_id":"py_Api",
                "fromApp":"ZG001",
                "grant_type":"authorization_code",
                "code":code
            },
            verify=False
        )
        response_tk_json = responsetk.json();
        
        if response_tk_json.get('responseStatus') == 'error':
            message = response_tk_json.get('errorMsg')
            if message == 'error':
                raise MagicHomeApiException("get access token failed")
            else:
                raise MagicHomeApiException(message)

        SESSION.accessToken = response_tk_json.get('access_token')
        SESSION.refreshToken = response_tk_json.get('refresh_token')
        SESSION.expireTime = int(time.time()) + response_tk_json.get('expires_in')
        
        areaCode = SESSION.accessToken[0: 2]
        if areaCode == 'EU':
            SESSION.region = 'eu'
        elif areaCode == 'CN':
            SESSION.region = 'cn'
        else:
            SESSION.region = 'us'




    def check_access_token(self):
        if SESSION.username == '' or SESSION.password == '':
            raise MagicHomeApiException("can not find username or password")
            return
        if SESSION.accessToken == '' or SESSION.refreshToken == '':
            self.get_access_token()
        elif SESSION.expireTime <= REFRESHTIME + int(time.time()):
            self.refresh_access_token()




    def refresh_access_token(self):
        data = "grant_type=refresh_token&refresh_token="+SESSION.refreshToken
        response = requests.get(
            (MAGHCHOMECLOUDURL + '/authorizationToken').format(SESSION.region)
            + "?" + data)
        response_json = response.json()
        if response_json.get('responseStatus') == 'error':
            raise MagicHomeApiException('refresh token failed')

        SESSION.accessToken = response_json.get('access_token')
        # print("refresh_access_token accessToken: " , accessToken)
        SESSION.refreshToken = response_json.get('refresh_token')
        # print("refresh_access_token refreshToken: " , refreshToken)
        SESSION.expireTime = int(time.time()) + response_json.get('expires_in')





    # Update of training equipment
    def poll_devices_update(self):
        self.check_access_token()
        return self.discover_devices(self)







    def discovery(self):
        response = self._request(self,'DiscoveryDevices', 'MagicHome.Python.API',None,{})
        print("discovery response: " , response)
        if response is not None :
            return response
        return None







    def discover_devices(self):
        devices = self.discovery(self)
        if not devices:
            return None
        SESSION.devices = []
        
        for device in devices:
            SESSION.devices.extend(get_magichome_device(device, self))
        return devices




    def get_devices_by_type(self, dev_type):
        device_list = []
        for device in SESSION.devices:
            if device.dev_type() == dev_type:
                device_list.append(device)





    def get_all_devices(self):
        return SESSION.devices




    def md5(str):
        m = hashlib.md5()
        s = str.encode(encoding='utf-8')
        m.update(s)
        result = m.hexdigest()
        return result
        
        
        
        
    def get_device_by_id(self, dev_id):
        for device in SESSION.devices:
            if device.object_id() == dev_id:
                return device
        return None





    def device_control(self, devId, action, param=None, namespace='control'):
        if param is None:
            param = {}
        response = self._request(action, namespace, devId, param)
        if response and response['header']['code'] == 'SUCCESS':
            success = True
        else:
            success = False
        return success,response




    def _request(self, name, namespace, devId=None, payload={}):
        headers = {
            'Content-Type': 'application/json;charset=UTF-8;'
        }
        
        header = {
            'name': name,
            'namespace': namespace,
            'payloadVersion': 1,
        }
        
        print("_request SESSION.accessToken:", SESSION.accessToken)
        payload ={
            "accessToken": SESSION.accessToken,
            "deviceId": devId
        }
        data = {
            'header': {
                'name': name,
                'namespace': namespace,
                'payloadVersion': 1,
                'messageId': str(uuid.uuid1()),
            },
            'payload': payload
        }
        response = requests.post(
            (MAGHCHOMECLOUDURL+'/mainControlEnter/ZG001').format(SESSION.region),
            json = data,
            headers = headers,
            verify=False
        )
        
        response_json = response.json()
        if response_json is not None :
            if 'payload' in response_json :
                if 'errorCode' in response_json['payload'] :
                    _LOGGER.error("discover ERROR Code:", response_json['payload']['errorCode'])
                    return None
        
        if name == "DiscoveryDevices" :
            if 'payload' in response_json :
                if 'devices' in response_json['payload'] :
                    return response_json['payload']['devices']
            else:
                return None
        # elif name == "Other":
            # print(name)
        
        return response_json
        
        
        


class MagicHomeApiException(Exception):
    pass

