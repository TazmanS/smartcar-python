import paho.mqtt.client as mqtt


MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "/smartcar/cmd"


class MqttService:
    def __init__(
        self,
        broker: str = MQTT_BROKER,
        port: int = MQTT_PORT,
        topic: str = MQTT_TOPIC,
    ):
        self.topic = topic
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self._client.connect(broker, port, 60)
        self._client.loop_start()
        print(f"MQTT connected to {broker}:{port}")

    def publish(self, command: str) -> None:
        self._client.publish(self.topic, command)
        print(f"Command sent → {self.topic}: {command}")

    def disconnect(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()
        print("MQTT disconnected")
