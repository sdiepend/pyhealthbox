import requests
import logging
import json
from socket import *

_LOGGER = logging.getLogger(__name__)


class Healthbox():

    def __init__(self, ip_address=""):
        if ip_address == "":
            self.ip_address = self.discover_healthbox()
        else:
            self.ip_address = ip_address

    def discover_healthbox(self):
        ip = ''
        serial = ''
        # Create a UDP socket for device discovery
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        sock.settimeout(5)

        server_address = ('255.255.255.255', 49152)
        message = 'RENSON_DEVICE/JSON?'

        discovered_devices = []
        try:
            sent = sock.sendto(message.encode(), server_address)
            while True:
                data, server = sock.recvfrom(4096)
                if data.decode('UTF-8'):
                    discovered_devices.append(json.loads(data))
                else:
                    print('Verification failed')
                print('Trying again...')

        except Exception as ex:
            if len(discovered_devices) == 0:
                _LOGGER.error('Error during discovery for serial: {0}'.format(ex))

        finally:
            sock.close()

        for device in discovered_devices:
            serial = device.get('serial')
            ip = device.get('IP')

        if ip == '':
            _LOGGER.error('Error during discovery for serial: {0}'.format(serial))
        return ip

    def get_global_air_quality_index(self):
        endpoint = 'http://' + self.ip_address + '/v1/api/data/current'
        hb_response = requests.get(url=endpoint).json()
        gaqi = hb_response['sensor'][0]['parameter']['index']['value']
        return gaqi
