import os
import logging

os.makedirs("log", exist_ok=True)

logger = logging.getLogger("transcription_controller")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("log/controller.log")
file_handler.setLevel(logging.INFO)


formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(file_handler)