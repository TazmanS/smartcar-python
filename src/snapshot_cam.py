import requests
import cv2
import numpy as np

from src.mqtt_service import MqttService


SNAPSHOT_URL = "http://192.168.31.49/snapshot"

# How far (in pixels) the line centroid must be from center to turn
TURN_THRESHOLD = 20


class SnapshotCamService:
    def __init__(
        self,
        url: str = SNAPSHOT_URL,
        mqtt: MqttService | None = None,
    ):
        self.url = url
        self._mqtt = mqtt or MqttService()

    # ------------------------------------------------------------------
    # Camera
    # ------------------------------------------------------------------

    def fetch(self) -> bytes:
        response = requests.get(self.url, stream=True, timeout=(5, 10))
        print("status:", response.status_code)
        print("content-type:", response.headers.get("Content-Type"))

        if response.status_code != 200:
            raise RuntimeError(f"Bad status code: {response.status_code}")

        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                chunks.append(chunk)
                total += len(chunk)
                print("received bytes:", total)

        data = b"".join(chunks)
        print("final bytes:", len(data))

        if not data:
            raise RuntimeError("No data received from camera")

        return data

    def decode(self, data: bytes) -> np.ndarray:
        img_array = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if frame is None:
            raise RuntimeError("Failed to decode image")
        print("Decoded:", frame.shape)
        return frame

    # ------------------------------------------------------------------
    # Line detection
    # ------------------------------------------------------------------

    def detect_line(self, frame: np.ndarray) -> int | None:
        """
        Analyse the bottom-centre strip of the frame and return the
        horizontal centroid (x) of the detected line, or None if not found.

        Assumes a dark line on a light background (invert threshold if needed).
        """
        h, w = frame.shape[:2]

        # Region of interest: bottom 20% of the image, full width
        roi_top = int(h * 0.80)
        roi = frame[roi_top:h, 0:w]

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Binary threshold – dark line on light background
        _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY_INV)

        # Find the centroid of all white (line) pixels
        moments = cv2.moments(thresh)
        if moments["m00"] == 0:
            return None  # no line found

        cx = int(moments["m10"] / moments["m00"])
        print(f"Line centroid x={cx}, frame centre={w // 2}")
        return cx

    # ------------------------------------------------------------------
    # Command decision
    # ------------------------------------------------------------------

    def decide_command(self, cx: int | None, frame_width: int) -> str:
        """Return a driving command based on line centroid position."""
        if cx is None:
            return "stop"

        center = frame_width // 2
        error = cx - center

        if error < -TURN_THRESHOLD:
            return "left"
        elif error > TURN_THRESHOLD:
            return "right"
        else:
            return "forward"

    def show_frame(self, frame: np.ndarray, cx: int | None, command: str) -> None:
        """Display current frame with guiding overlays."""
        view = frame.copy()
        h, w = view.shape[:2]
        center_x = w // 2

        # Image center line
        cv2.line(view, (center_x, 0), (center_x, h), (255, 0, 0), 2)

        # Detected line centroid marker
        if cx is not None:
            cv2.circle(view, (cx, int(h * 0.9)), 8, (0, 255, 255), -1)

        cv2.putText(
            view,
            f"cmd: {command}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        cv2.imshow("SmartCar Camera", view)

    # ------------------------------------------------------------------
    # MQTT
    # ------------------------------------------------------------------

    def send_command(self, command: str) -> None:
        self._mqtt.publish(command)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        print("Starting snapshot loop — press Ctrl+C or 'q' to stop")
        try:
            while True:
                try:
                    data = self.fetch()
                    frame = self.decode(data)

                    cx = self.detect_line(frame)
                    command = self.decide_command(cx, frame.shape[1])
                    self.send_command(command)
                    self.show_frame(frame, cx, command)

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        print("Stopped by key 'q'")
                        break

                except Exception as e:
                    print(f"Frame error: {e}")

        except KeyboardInterrupt:
            print("Stopped by user")
        finally:
            cv2.destroyAllWindows()
            self._mqtt.disconnect()
