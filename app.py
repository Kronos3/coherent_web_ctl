from flask import Flask

from device_manager import DeviceEvent
from hardware import TCP_ADDRESS
from log import logger
from ipc import TCPStartpointIPC

ipc_endpoint = TCPStartpointIPC(TCP_ADDRESS)
app = Flask(__name__)


@app.route('/log')
def get_log():
    with open(logger.get_path(), 'r') as read_log:
        return read_log.read()


@app.route('/get-state/<device_id>')
def get_state(device_id: int):
    state = ipc_endpoint.send_ipc(device_id, DeviceEvent.GET_STATE)

    if state.status:
        return 200, state.response
    else:
        return 500, state.response


@app.route('/turn-on/<device_id>')
def turn_on(device_id: int):
    state = ipc_endpoint.send_ipc(device_id, DeviceEvent.SWITCH_ON)

    if state.status:
        return 200, state.response
    else:
        return 500, state.response


@app.route('/turn-off/<device_id>')
def turn_on(device_id: int):
    state = ipc_endpoint.send_ipc(device_id, DeviceEvent.SWITCH_OFF)

    if state.status:
        return 200, state.response
    else:
        return 500, state.response


if __name__ == '__main__':
    app.run()
