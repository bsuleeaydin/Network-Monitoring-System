import logging
import os
from logging.handlers import RotatingFileHandler

# logs klasörü yoksa oluştur
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "app.log")


def setup_logging():
    logger = logging.getLogger("network_monitor")
    logger.setLevel(logging.INFO)

    # Aynı handler'ların tekrar tekrar eklenmesini önle (uvicorn --reload ile önemli)
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Dosyaya yazan handler (dosya 5MB'ı geçerse otomatik döner, en fazla 3 yedek tutar)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Terminale de yazan handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()