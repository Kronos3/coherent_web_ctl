from flask import Flask, jsonify, render_template

from device import DeviceEvent
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
    try:
        state = ipc_endpoint.send_ipc(device_id, DeviceEvent.GET_STATE)
    except ConnectionError:
        return "Failed to connect", 500

    return jsonify(state.response)


@app.route('/turn-on/<device_id>')
def turn_on(device_id: int):
    try:
        state = ipc_endpoint.send_ipc(device_id, DeviceEvent.SWITCH_ON)
    except ConnectionError:
        return "Failed to connect", 500

    return jsonify(state.response)


@app.route('/get-metadata/<device_id>')
def get_metadata(device_id: int):
    try:
        state = ipc_endpoint.send_ipc(device_id, DeviceEvent.METADATA)
    except ConnectionError:
        return "Failed to connect", 500

    return jsonify(state.response)


@app.route('/turn-off/<device_id>')
def turn_off(device_id: int):
    try:
        state = ipc_endpoint.send_ipc(device_id, DeviceEvent.SWITCH_OFF)
    except ConnectionError:
        return "Failed to connect", 500

    return jsonify(state)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
