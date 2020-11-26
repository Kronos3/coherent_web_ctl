from device_manager import HardwareDeviceManager
from gpio_control import Switch, Board
from ipc import TCPEndpoint

COHERENT_PIN = 12
HERCULES_PIN = 14

TCP_ADDRESS = "/tmp/cdei.hardware.sock"


def main(_args) -> int:
    manager = HardwareDeviceManager()

    manager.register_device("coherent_pwr", Switch(COHERENT_PIN, "coherent_pwr"))
    manager.register_device("hercules_pwr", Switch(COHERENT_PIN, "hercules_pwr"))

    # Don't register board, its an internal device
    board = Board()
    board.add_hardware(manager.get_device("coherent_pwr"))
    board.add_hardware(manager.get_device("hercules_pwr"))
    board.hardware_init()

    ipc = TCPEndpoint(TCP_ADDRESS, manager)
    ipc.start()

    board.hardware_cleanup()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
