from typing import List, Dict, Optional

from device import Device, DeviceEvent
from log import logger


class DeviceManager(Device):
    name_to_devices: Dict[str, Device]
    device_to_id: Dict[Device, int]
    id_to_device: List[Device]
    id_counter: int

    def __init__(self):
        super().__init__()

        self.name_to_devices = {}
        self.device_to_id = {}
        self.id_to_device = []

        self.id_counter = 0

        self.register_event(DeviceEvent.METADATA, self.get_metadata)
        self.register_device("self", self)

    def register_device(self, name: str, device: Device) -> int:
        """
        Add a device to the registry
        :param name: key to query device by
        :param device: device to register
        :return: unique id of device, -1 for invalid
        """

        if name in self.name_to_devices and device != self.name_to_devices[name]:
            logger.warning("Device with name '%s' is already registered as %s" % (name, self.name_to_devices[name]))
            return -1

        if name in self.name_to_devices and device == self.name_to_devices[name]:
            logger.warning("Duplicated register of the same device %s: %s" % (name, device))
            return -1

        device_id = self.id_counter
        logger.debug("Registering hardware device '%s' as %s (id %d)" % (name, device, device_id))

        self.name_to_devices[name] = device
        self.device_to_id[device] = device_id
        self.id_to_device.append(device)
        self.id_counter += 1

        return device_id

    def get_device_id(self, device: Device) -> int:
        if device not in self.device_to_id:
            logger.error("Device %s is not a registered device" % device)
            return -1

        return self.device_to_id[device]

    def get_device_by_id(self, _id: int) -> Optional[Device]:
        if _id < 0:
            logger.error("Invalid device ID %d" % _id)
            return None
        if _id >= len(self.id_to_device):
            logger.error("Device with ID %d is not registered" % _id)
            return None

        return self.id_to_device[_id]

    def get_device(self, name: str) -> Optional[Device]:
        """
        Get a device registered with a key
        :param name: key of the device
        :return: Device with key, None if not found
        """

        if name not in self.name_to_devices:
            logger.error("Device with name '%s' is not registered" % name)
            return None

        return self.name_to_devices[name]

    def get_metadata(self, *_args):
        devices_serial = []
        for device in self.id_to_device[1:]:
            if device.check_dispatch(DeviceEvent.METADATA):
                devices_serial.append(device.dispatch(DeviceEvent.METADATA)[1])
            else:
                devices_serial.append(str(device))

        return {
            'name': 'self',
            'devices': devices_serial,
            'id_offset': 1
        }

    def hardware_init(self):
        pass

    def hardware_cleanup(self):
        pass
