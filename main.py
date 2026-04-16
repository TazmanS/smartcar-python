from src.mqtt_service import MqttService
from src.snapshot_cam import SnapshotCamService


def main():
    mqtt = MqttService()
    service = SnapshotCamService(mqtt=mqtt)
    service.run()


if __name__ == "__main__":
    main()
