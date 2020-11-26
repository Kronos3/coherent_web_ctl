import json
import os
import socket
from abc import ABC, abstractmethod
from dataclasses import dataclass

from device import DeviceEvent
from device_manager import DeviceManager
from log import logger


class Communication(ABC):
    @abstractmethod
    def serialize(self) -> bytes: ...

    @staticmethod
    @abstractmethod
    def parse(data: bytes) -> 'Communication': ...


@dataclass(frozen=True)
class Message(Communication):
    event: DeviceEvent
    device_id: int
    args: object = None

    def serialize(self) -> bytes:
        json_data = json.dumps({
            'event': self.event,
            'device_id': self.device_id,
            'args': self.args
        })

        return len(json_data).to_bytes(4, byteorder='big', signed=False) \
                + json_data.encode('utf-8')

    @staticmethod
    def parse(data: bytes) -> 'Message':
        d = json.loads(data.decode('utf-8'))

        return Message(d['event'],
                       int(d['device_id']),
                       d['args'])


@dataclass(frozen=True)
class Response(Communication):
    status: bool
    response: object

    def serialize(self) -> bytes:
        json_data = json.dumps({
            'status': self.status,
            'response': self.response,
        })

        return len(json_data).to_bytes(4, byteorder='big', signed=False) \
               + json_data.encode('utf-8')

    @staticmethod
    def parse(data: bytes) -> 'Response':
        d = json.loads(data.decode('utf-8'))
        return Response(d['status'], d['response'])


class IPCEndpoint(ABC):
    hardware_manager: DeviceManager

    def __init__(self, hardware_manager: DeviceManager):
        self.hardware_manager = hardware_manager

    def receive_ipc(self, message: Message) -> Response:
        target_device = self.hardware_manager.get_device_by_id(message.device_id)
        if target_device is None:
            logger.error("Invalid device ID: '%d'" % message.device_id)
            return Response(False, None)

        logger.debug("Received %s to '%s' args: %s" % (DeviceEvent(message.event), target_device, message.args))
        status, return_value = target_device.dispatch(message.event, message.args)
        return Response(status, return_value)

    @abstractmethod
    def start(self): ...

    @abstractmethod
    def run(self): ...


class TCPEndpoint(IPCEndpoint):
    unix_endpoint: bool
    sock: socket.socket

    def __init__(self, address, manager: DeviceManager):
        super().__init__(manager)
        self.address = address

        if isinstance(address, str):
            self.unix_endpoint = True
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)

            try:
                os.unlink(self.address)
            except OSError:
                if os.path.exists(self.address):
                    raise
        else:
            self.unix_endpoint = False
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    @staticmethod
    def _read_message(client_sock: socket.socket) -> Message:
        # Read the length of the message
        message_len = int.from_bytes(client_sock.recv(4), byteorder='big', signed=False)

        # Read and parse the message
        return Message.parse(client_sock.recv(message_len))

    def run(self):
        while True:
            client, address = self.sock.accept()

            if not self.unix_endpoint:
                # Connections to unix sockets have no address
                logger.debug("Connection from %s" % address)

            response = self.receive_ipc(self._read_message(client))
            client.sendall(response.serialize())
            client.close()

    def start(self):
        self.sock.bind(self.address)
        self.sock.listen(32)

        keep_running = True
        while keep_running:
            try:
                self.run()
            except KeyboardInterrupt:
                logger.info("Shutting down IPC")
                keep_running = False
            except Exception as e:
                logger.error(e)

        self.sock.close()


class IPCStartpoint(ABC):
    def send_ipc(self, device: int, event: DeviceEvent, *args) -> Response:
        return self.send_message(Message(event, device, args))

    @abstractmethod
    def send_message(self, message: Message): ...


class TCPStartpointIPC(IPCStartpoint):
    def __init__(self, server_address):
        self.address = server_address

    @staticmethod
    def _read_response(client_sock: socket.socket) -> Response:
        # Read the length of the message
        response_len = int.from_bytes(client_sock.recv(4), byteorder='big', signed=False)

        # Read and parse the message
        return Response.parse(client_sock.recv(response_len))

    def send_message(self, message: Message) -> Response:
        """

        :rtype: object
        """
        if isinstance(self.address, str):
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

        s.connect(self.address)
        s.send(message.serialize())
        res = self._read_response(s)
        s.close()

        return res
