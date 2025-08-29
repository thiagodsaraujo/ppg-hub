# app/core/logging.py
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,  # 👈 mostra debug, info, warning, error
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
