from django.core.management.base import BaseCommand
from modules.toll_record.ia.videoCapture import LicensePlateDetector


class Command(BaseCommand):
    help = 'Inicia el monitor de detección de matrículas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--camera',
            type=int,
            default=1,
            help='Índice de la cámara a utilizar'
        )
        parser.add_argument(
            '--port',
            type=str,
            default='COM1',
            help='Puerto serial para la conexión Arduino'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Iniciando monitor de detección de matrículas...')
        )

        detector = LicensePlateDetector(
            camera_index=options['camera'],
            serial_port=options['port']
        )

        try:
            detector.run()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Monitor detenido por el usuario'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error en el monitor: {str(e)}')
            )
