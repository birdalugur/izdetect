import time
from core.base import Service
from core.interfaces import VideoSource, MessageBroker
from services.processors.image_processor import ImageProcessor

class FrameProducer(Service):
    def __init__(
        self,
        video_source: VideoSource,
        message_broker: MessageBroker,
        output_queue: str,
        camera_id: str,
    ):
        super().__init__(message_broker)
        self.video_source = video_source
        self.output_queue = output_queue
        self.camera_id = camera_id
        self.is_connected = False
        self.stop_signal = False

    def stop(self):
        """Kamera bağlantısını kes ve işlemi durdur."""
        self.stop_signal = True
        self.is_connected = False
        print(f"Stopping FrameProducer for camera {self.camera_id}...")

    def run(self, encoding_method="binary"):
        print(f"[{self.camera_id}] FrameProducer started.")

        # Outer loop handles connection/reconnection
        while not self.stop_signal:
            success = self.video_source.open()
            if not success:
                print(f"[{self.camera_id}] Error opening video source. Retrying in 2s...")
                time.sleep(2)
                continue

            self.is_connected = True
            print(f"[{self.camera_id}] Connected.")

            not_ret_count = 0

            # Inner loop handles frame reading
            while not self.stop_signal:
                ret, frame = self.video_source.read()
                if not ret:
                    not_ret_count += 1
                    # Log every 10 failures
                    if not_ret_count % 10 == 0:
                        print(f"[{self.camera_id}] No frames, retrying {not_ret_count}...")

                    # If we fail enough times, assume connection lost
                    if not_ret_count > 5:
                        print(f"[{self.camera_id}] Connection lost. Reconnecting...")
                        break

                    time.sleep(0.1)
                    continue

                # Reset failure counter on success
                not_ret_count = 0

                try:
                    image_bytes = ImageProcessor.encode_img(
                        frame, encoding_method=encoding_method
                    )
                    if self.message_broker:
                        self.message_broker.lpush(self.output_queue, image_bytes)
                except Exception as e:
                    print(f"[{self.camera_id}] Error processing frame: {e}")

            self.video_source.release()
            self.is_connected = False

            if not self.stop_signal:
                time.sleep(1)

        print(f"[{self.camera_id}] FrameProducer stopped.")
