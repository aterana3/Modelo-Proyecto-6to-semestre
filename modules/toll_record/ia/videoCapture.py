import cv2
import easyocr
import numpy as np
import re
import threading
from modules.toll_record.ia.serialConnection import SerialConnection
from django.conf import settings
from django.utils import timezone
from modules.toll_record.models import TollRecord


class LicensePlateDetector:
    def __init__(self, camera_index=1, serial_port='COM1'):
        self.reader = easyocr.Reader(['es'])
        self.plate_regex = r'^[A-Za-z]{3}-\d{3}$'
        self.camera_index = camera_index
        self.cap = None
        self.is_capturing = False
        self.serial_conn = SerialConnection(serial_port)
        self.running = True
        self.image_dir = os.path.join(settings.MEDIA_ROOT, 'toll_records')

        os.makedirs(self.image_dir, exist_ok=True)

    def start(self):
        self.serial_conn.connect()
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print("Error: No se pudo abrir la cámara.")
            return False
        return True

    def process_frame(self, frame):
        frame = cv2.flip(frame, -1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.blur(gray, (3, 3))
        canny = cv2.Canny(gray, 150, 200)
        kernel = np.ones((3, 3), np.uint8)
        canny = cv2.dilate(canny, kernel, iterations=1)
        cnts, _ = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        for c in cnts:
            area = cv2.contourArea(c)
            x, y, w, h = cv2.boundingRect(c)
            epsilon = 0.09 * cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, epsilon, True)

            if len(approx) == 4 and area > 9000:
                aspect_ratio = float(w) / h
                if aspect_ratio > 2.4:
                    plate = gray[y:y + h, x:x + w]
                    text = self.reader.readtext(plate, detail=0)
                    if text:
                        plate_text = ''.join(text)
                        plate_text = plate_text.replace(" ", "")
                        plate_text = plate_text.replace("-", "")
                        plate_text = plate_text[:3] + '-' + plate_text[3:]
                        if re.match(self.plate_regex, plate_text):
                            return plate_text
        return None

    def read_serial_commands(self):
        while self.running:
            command = self.serial_conn.read_data()
            if command == "CAPTURE":
                print("Comando CAPTURE recibido. Iniciando captura...")
                self.is_capturing = True

    def run(self):
        if not self.start():
            return

        serial_thread = threading.Thread(target=self.read_serial_commands, daemon=True)
        serial_thread.start()

        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error al capturar imagen.")
                    continue

                if self.is_capturing:
                    plate_text = self.process_frame(frame)
                    if plate_text:
                        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                        image_filename = f'{plate_text}_{timestamp}.jpg'
                        image_path = os.path.join('toll_records', image_filename)
                        full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)

                        cv2.imwrite(full_image_path, frame)
                        print(f"Imagen guardada en: {full_image_path}")

                        TollRecord.objects.create(
                            license_plate=plate_text,
                            pass_date=timezone.now(),
                            location_id=settings.LOCATION_ID,
                            amount_due=settings.AMOUNT_DUE,
                            image=image_path
                        )
                        self.serial_conn.send_data("SUCCESS")
                        self.is_capturing = False
        except KeyboardInterrupt:
            print("\nDetención solicitada por el usuario")
        finally:
            self.running = False
            self.cap.release()
