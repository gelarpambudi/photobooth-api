from flask import Flask
from flask_cors import CORS
import os
import logging
import confuse

app = Flask(__name__)
CORS(app)
app_config = confuse.Configuration("photobooth_py", __name__)
app_config.set_file(os.environ['CONFIG_PATH'])

try:
    app.config["IMG_SRC_BASE_DIR"] = app_config["IMG_SRC_BASE_DIR"].get()
    app.config["IMG_RESULT_BASE_DIR"] = app_config["IMG_RESULT_BASE_DIR"].get()
    app.config["IMG_FRAME_BASE_DIR"] = app_config["IMG_FRAME_BASE_DIR"].get()
    app.config["IMG_FRAME_ASSETS_DIR"] = app_config["IMG_FRAME_ASSETS_DIR"].get()
    app.config["EMAIL_USERNAME"] = app_config["EMAIL_USERNAME"].get()
    app.config["EMAIL_PASSWD"] = app_config["EMAIL_PASSWD"].get()
    app.config["AVAILABLE_EFFECT"] = app_config["AVAILABLE_EFFECT"].as_str_seq()
    app.config["AVAILABLE_8_FRAME"] = app_config["AVAILABLE_8_FRAME"].as_str_seq()
    app.config["AVAILABLE_8_FRAME_ELLIPSE"] = app_config["AVAILABLE_8_FRAME_ELLIPSE"].as_str_seq()
    app.config["AVAILABLE_6_FRAME"] = app_config["AVAILABLE_6_FRAME"].as_str_seq()
    app.config["SMTP_SERVERNAME"] = app_config["SMTP_SERVERNAME"].get()
    app.config["SMTP_SERVERPORT"] = app_config["SMTP_SERVERPORT"].get(int)
    app.config["PRINTER_NAME"] = app_config["PRINTER_NAME"].get()
    logging.info("Start loading configuration...")
except Exception as e:
    logging.error("Error loading configuration", exc_info=True)