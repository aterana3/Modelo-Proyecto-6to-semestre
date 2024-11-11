from django.core.management.base import BaseCommand
from django.conf import settings
import cv2
import easyocr
import numpy as np
import re
import signal
import sys
from modules.toll_record.serialConnection import SerialConnection
from modules.toll_record.models import TollRecord
from django.utils import timezone


class Command(BaseCommand):
    help = 'Start monitoring Arduino signals and capture images'

    def __init__(self):
        super().__init__()
        self.running = False
        self.connection = None
        self.reader = easyocr.Reader(['es'])

    def handle(self, *args, **options):
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        try:
            self.start_monitor()
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            self.cleanup()

    def signal_handler(self, signum, frame):
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        self.running = False
        if self.connection:
            self.connection.send_data("EXIT\n")
            self.connection.disconnect()
        self.stdout.write(self.style.SUCCESS('Monitor stopped successfully'))

    def start_monitor(self):
        self.stdout.write(self.style.SUCCESS('Starting Arduino monitor...'))

        self.connection = SerialConnection(port='COM3', baudrate=9600)
        self.connection.connect()
        plate_regex = r'^[A-Za-z]{3}-\d{3}$'

        while self.running:
            try:
                message = self.connection.read_data()
                if message == "CAPTURE":
                    print("Capturing image...")
                    cap = cv2.VideoCapture(settings.CAMERA_PORT)
                    ret, frame = cap.read()
                    if not ret:
                        continue

                    frame = cv2.flip(frame, -1)
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray = cv2.blur(gray, (3, 3))
                    canny = cv2.Canny(gray, 150, 200)

                    kernel = np.ones((3, 3), np.uint8)
                    canny = cv2.dilate(canny, None, iterations=1)

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

                                plate_text = ' '.join(text)
                                plate_text = plate_text.replace(" ", "")
                                plate_text = plate_text.replace("-", "")
                                plate_text = plate_text[:3] + '-' + plate_text[3:]

                                if re.match(plate_regex, plate_text):
                                    image_path = f'toll_records/{plate_text}.jpg'
                                    cv2.imwrite(f'{settings.MEDIA_ROOT}/{image_path}', frame)

                                    TollRecord.objects.create(
                                        license_plate=plate_text,
                                        pass_date=timezone.now(),
                                        location_id=settings.LOCATION_ID,
                                        amount_due=settings.AMOUNT_DUE,
                                        image=image_path
                                    )
                                    self.connection.send_data("SUCCESS\n")
                                    self.stdout.write(self.style.SUCCESS(f'Captured plate: {plate_text}'))
                        cv2.imshow("Camera Feed", frame)
                    cap.release()

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing frame: {str(e)}'))
                continue

        # Cerrar la ventana de la cámara al finalizar
        cv2.destroyAllWindows()
