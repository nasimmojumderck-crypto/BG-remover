from io import BytesIO

from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
from rembg import remove, new_session

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
session = None


def get_session():
    global session
    if session is None:
        session = new_session("isnet-general-use")
    return session


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    if "image" not in request.files:
        return jsonify({"error": "কোনো ফাইল পাওয়া যায়নি"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "ফাইল নির্বাচন করা হয়নি"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "শুধু PNG, JPG, JPEG বা WEBP ফাইল দিন"}), 400

    try:
        input_image = Image.open(file.stream)
        input_image = input_image.convert("RGBA") if input_image.mode != "RGBA" else input_image
        output_image = remove(input_image, session=get_session())

        output_buffer = BytesIO()
        output_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        base_name = file.filename.rsplit(".", 1)[0]
        return send_file(
            output_buffer,
            mimetype="image/png",
            as_attachment=True,
            download_name=f"{base_name}_no_bg.png",
        )
    except Exception:
        return jsonify({"error": "ইমেজ প্রসেস করা যায়নি, অন্য ফাইল দিয়ে চেষ্টা করুন"}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
