import json
import os
import logging
from flask import jsonify, request, url_for
from config import app
from image_processing import *
from send_email import *
from printer_utils import *


@app.route("/api/generate-image", methods=["POST"])
def generate_image_api():
    content = request.json
    tx_id = content["tx_id"]
    frame_id = content["frame_id"]
    source_path = os.path.join(app.config["IMG_SRC_BASE_DIR"], tx_id)
    result_path = os.path.join(app.config["IMG_RESULT_BASE_DIR"], tx_id)
    
    try:

        for effect in app.config["AVAILABLE_EFFECT"]:
            os.makedirs(f"{result_path}/{effect}", exist_ok=True)
        
        img_list = os.listdir(source_path)
        logging.info(f"Applying filter for {tx_id} images")
        for img_file in img_list:
            img_file_path = os.path.join(source_path, img_file)

            img_np = load_image(img_file_path)
            apply_all_effect(img_np, result_path, img_file)
        
        available_filter_result = os.listdir(result_path)
        logging.info(f"Compiling images for {tx_id}")
        for effect_dir in available_filter_result:
            compiled_np = compile_frame(
                frame_id=frame_id,
                src_img_path=os.path.join(result_path,effect_dir),
                frame_base_dir=app.config['IMG_FRAME_BASE_DIR']
            )
            save_image(compiled_np, os.path.join(result_path, f"{effect_dir}/compiled.jpg"))

            generate_gif(
                os.path.join(result_path,effect_dir),
                os.path.join(result_path, f"{effect_dir}/compiled.gif")
            )
        data = {
            "status_code": 200,
            "message": "Success",
            "result_dir": [ f"http://localhost:8080/static/res_image/{tx_id}/{x}/compiled.jpg" for x in os.listdir(result_path) ],
            "error": "null"
        }
        return jsonify(data), 200
    except Exception as e:
        data = {
            "status_code": 503,
            "message": "Cannot process the image",
            "error": e
        }
        return jsonify(data), 503


@app.route("/api/get-frame", methods=["GET"])
def get_frame_api():
    frame_list = []
    for frame in app.config['AVAILABLE_FRAME']:
        frame_list.append(
            os.path.join(app.config['IMG_FRAME_BASE_DIR'], frame)
        )
    data = {
        "status_code": 200,
        "message": "Success",
        "frame_list": frame_list
    }
    return jsonify(data), 200


@app.route("/api/send-email", methods=['POST'])
def send_email_api():
    content = request.json
    tx_id = content['tx_id']
    effect = content['effect']
    email = content['email']
    recipient_name = content['recipient_name']

    composed_email = compose_email(recipient_name, [email], tx_id, effect)

    try:
        send_email(
            composed_email,
            email,
            app.config['SMTP_SERVERNAME'],
            app.config['SMTP_SERVERPORT']
            )
        data = {
            "status_code": 200,
            "message": "Success",
            "error": "null"
        }
        return jsonify(data), 200
    except Exception as e:
        data = {
            "status_code": 503,
            "message": "Failed to send email",
            "error": f"{e}"
        }
        return jsonify(data), 503


@app.route("/api/print-image", methods=['POST'])
def print_image_api():
    content = request.json
    tx_id = content['tx_id']
    effect = content['effect']

    result_path = os.path.join(app.config["IMG_RESULT_BASE_DIR"], tx_id)

    try:
        img_file = os.path.join(result_path, f"{effect}/compiled.jpg")
        printer_name = get_printer_name()
        dc = get_device_context(printer_name)
        print_image(img_file, dc)

        data = {
            "status_code": 200,
            "message": "Success",
            "error": "null"
        }
        return jsonify(data), 200
    except Exception as e:
        data = {
            "status_code": 503,
            "message": "Failed to print image",
            "error": f"{e}"
        }
        return jsonify(data), 503


@app.route("/static/res_image/<tx_id>/effect", methods=["GET"])
def image_url(tx_id, effect):
    return "<img src=" + url_for('static', filename=f'{tx_id}/{effect}/compiled.jpg') + ">"


if __name__ == "__main__":
    app.run(host='localhost', port='8080', debug=True)