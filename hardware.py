from device_manager import HardwareDeviceManager
from dummy_device import DummyBoard, DummySwitch
from ipc import TCPEndpoint

COHERENT_PIN = 12
HERCULES_PIN = 14

TCP_ADDRESS = "/tmp/cdei.hardware.sock"


def main(_args) -> int:
    manager = HardwareDeviceManager()

    manager.register_device("coherent_pwr", DummySwitch(COHERENT_PIN, "coherent_pwr"))
    manager.register_device("hercules_pwr", DummySwitch(COHERENT_PIN, "hercules_pwr"))

    # Don't register board, its an internal device
    board = DummyBoard()
    board.hardware_init()
    board.add_hardware(manager.get_device("coherent_pwr"))
    board.add_hardware(manager.get_device("hercules_pwr"))

    ipc = TCPEndpoint(TCP_ADDRESS, manager)
    ipc.start()

    board.hardware_cleanup()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
