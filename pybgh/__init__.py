"""BGH Smart devices API client"""
import requests

_BASE_URL = 'https://bgh-services.solidmation.com'
_API_URL = "%s/1.0" % _BASE_URL

FAN_MODE = {
    'slow': 1,
    'mid': 2,
    'high': 3,
    'auto': 254,
    'no_change': 255
}

MODE = {
    'off': 0,
    'cool': 1,
    'heat': 2,
    'dry': 3,
    'fan': 4,
    'auto': 254,
    'no_change': 255
}

class BghClient():
    """BGH client implementation"""

    def __init__(self, email, password):
        self.token = self._login(email, password)

    @staticmethod
    def _login(email, password):
        endpoint = "%s/control/LoginPage.aspx/DoStandardLogin" % _BASE_URL
        resp = requests.post(endpoint, json={'user': email, 'password': password})
        return resp.json()['d']

    def _request(self, endpoint, payload=None):
        if payload is None:
            payload = {}
        payload['token'] = {'Token': self.token}
        return requests.post(endpoint, json=payload)

    def _get_data_packets(self, home_id):
        endpoint = "%s/HomeCloudService.svc/GetDataPacket" % _API_URL
        payload = {
            'homeID': home_id,
            'serials': {
                'Home': 0,
                'Groups': 0,
                'Devices': 0,
                'Endpoints': 0,
                'EndpointValues': 0,
                'Scenes': 0,
                'Macros': 0,
                'Alarms': 0
            },
            'timeOut': 10000
        }
        resp = self._request(endpoint, payload)
        return resp.json()['GetDataPacketResult']

    def _parse_devices(self, data):
        devices = {}

        if data['Endpoints'] is None:
            return devices

        for idx, endpoint in enumerate(data['Endpoints']):
            device = {
                'device_id': endpoint['EndpointID'],
                'device_name': endpoint['Description'],
                'device_data': data['Devices'][idx],
                'raw_data': data['EndpointValues'][idx]['Values'],
                'data': self._parse_raw_data(data['EndpointValues'][idx]['Values']),
                'endpoints_data': endpoint
            }
            device['data']['device_model'] = device['device_data']['DeviceModel']
            device['data']['device_serial_number'] = device['device_data']['Address']

            devices[device['device_id']] = device

        return devices

    @staticmethod
    def _parse_raw_data(data):
        if data is None:
            return {}

        temperature = next(item['Value'] for item in data if item['ValueType'] == 13)
        if temperature:
            temperature = float(temperature)
            if temperature <= -50:
                temperature = None

        target_temperature = next(item['Value'] for item in data if item['ValueType'] == 20)
        if target_temperature:
            target_temperature = float(target_temperature)
            if target_temperature == 255:
                target_temperature = 20

        fan_speed = next(item['Value'] for item in data if item['ValueType'] == 15)
        if fan_speed:
            fan_speed = int(fan_speed)

        mode_id = next(item['Value'] for item in data if item['ValueType'] == 14)
        if mode_id:
            mode_id = int(mode_id)

        return {
            'temperature': temperature,
            'target_temperature': target_temperature,
            'fan_speed': fan_speed,
            'mode_id': mode_id
        }

    def get_homes(self):
        """Get all the homes of the account"""
        endpoint = "%s/HomeCloudService.svc/EnumHomes" % _API_URL
        resp = self._request(endpoint)
        return resp.json()['EnumHomesResult']['Homes']

    def get_devices(self, home_id):
        """Get all the devices of a home"""
        data = self._get_data_packets(home_id)
        devices = self._parse_devices(data)
        return devices

    def get_status(self, home_id, device_id):
        """Get the status of a device"""
        return self.get_devices(home_id)[device_id]

    def _set_device_mode(self, device_id, mode):
        mode['endpointID'] = device_id
        endpoint = "%s/HomeCloudCommandService.svc/HVACSetModes" % _API_URL
        resp = self._request(endpoint, mode)
        return resp

    def set_mode(self, device_id, mode, temp, fan='auto'):
        """Set the mode of a device"""
        config = {
            'desiredTempC': str(temp),
            'fanMode': FAN_MODE[fan],
            'flags': 255,
            'mode': MODE[mode]
        }
        return self._set_device_mode(device_id, config)
