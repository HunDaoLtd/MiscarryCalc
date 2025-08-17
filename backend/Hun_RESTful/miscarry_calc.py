from flask import Flask, request, jsonify, abort, send_from_directory
from flask_cors import CORS
import logging
from decrypt import decrypt_db_data
from mysql_op import DatabaseManager
from contextlib import contextmanager
from werkzeug.exceptions import HTTPException
import os
import json
import base64
from openai import OpenAI
import logging

# 获取一个日志记录器实例
logger = logging.getLogger(__name__)
logging.basicConfig(
    # filename="1_miscarry_calc_flask_error.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


client = OpenAI(api_key=os.environ["METACHAT_API_KEY"], base_url="https://llm-api.mmchat.xyz/v1")

UPLOAD_DIR = "/var/hundao/apps/1_miscarry_calc/images"  # 用于上传超声图

app = Flask(__name__)
# CORS(app)  # 允许所有跨域请求
# 全局 CORS 配置，允许所有方法和 HEAD 请求
CORS(
    app,
    resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    },
)
# logging.basicConfig(level=logging.INFO)


app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 限制上传文件的大小 1MB

db_info = None  # 先定义为 None
db_info = decrypt_db_data()  # 只在主入口调用


# Context manager for database connections
@contextmanager
def get_db_connection():
    global db_info
    db = DatabaseManager(host=db_info[2], user=db_info[0], password=db_info[1], db=db_info[3])
    try:
        db.connect()
        yield db
    finally:
        db.close()


# Global error handlers
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": e.description}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": e.description}), 404


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"An error occurred: {e}")
    if isinstance(e, HTTPException):
        return jsonify({"error": e.description}), e.code
    else:
        return jsonify({"error": "Internal Server Error"}), 500


@app.route("/images/<filename>", methods=["GET", "POST", "PUT", "OPTIONS"])
def upload_images(filename):
    # 处理预检请求
    if request.method == "OPTIONS":
        return jsonify({"status": "preflight"}), 200

    # 处理 GET 请求
    if request.method == "GET":
        file_path = os.path.join(UPLOAD_DIR, filename)

        # 检查文件是否存在
        if not os.path.exists(file_path):
            # 文件不存在 - 设置不缓存
            response = jsonify({"error": "File not found"}), 404
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response

        # 文件存在 - 设置 MIME 类型
        if filename.endswith(".avif"):
            mimetype = "image/avif"
        elif filename.endswith(".png"):
            mimetype = "image/png"
        elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
            mimetype = "image/jpeg"
        else:
            mimetype = "application/octet-stream"

        # 发送文件并设置 Content-Type
        response = send_from_directory(UPLOAD_DIR, filename, mimetype=mimetype)
        response.headers["Cache-Control"] = "public, max-age=31536000"  # 1年缓存
        return response

    # 处理上传
    if request.method in ["POST", "PUT"]:
        file_path = os.path.join(UPLOAD_DIR, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 检查是否有文件上传
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        try:
            file.save(file_path)
            return jsonify({"success": True}), 200
        except Exception as e:
            app.logger.error(f"Failed to save file {filename}: {e}")
            return jsonify({"error": "File save failed"}), 500


# 调用GPT进行图像分析
# 模型	输入 API 元点消耗比例	输出 API 元点消耗比例
# gpt-5	320	40  支持图像
# gpt-5-mini	1600	200  支持图像
# gpt-5-nano	8000	1000  支持图像
# gpt-5-chat-latest	320	40  支持图像
# gpt-4.1	200	50  支持图像
# gpt-4.1-mini	1000	250  支持图像
# gpt-4.1-nano	4000	1000  支持图像
# gpt-4o	160	40
# gpt-4o-mini	2666	666
# o3	200	50
# o4-mini	363.6	90.9  支持图像
# gpt-oss-120b	1600	533.2
# gpt-image-1	80(文本) / 26.6(图像)	6.66(图像)
#
# API 元点计算公式
# API 元点消耗 = 输入 Tokens / 输入 API 元点消耗比例 + 输出 Tokens / 输出 API 元点消耗比例
@app.route("/analysis/<filename>", methods=["GET"])
def analyze_image(filename):
    file_path = os.path.join(UPLOAD_DIR, filename)

    # 检查文件是否存在
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # 获取 Base64 编码
    base64_image = encode_image(file_path)

    prompt = """
分析超声结果，整理关键信息，仔细查找日期，仅输出标准 JSON 格式，且不包含多余的换行、空格或 BOM，格式如下：
{
    "孕囊大小": "",  # int，单位mm，多维时取平均值
    "胚芽长": "",    # int，单位mm
    "是否停育": "",  # bool
    "日期": ""       # str，格式"YYYY-MM-DD"
}
"""
    response = client.responses.create(
        # model="gpt-4.1",
        model="gpt-5-mini",
        # model="gpt-5-nano",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ],
    )
    # 直接返回 JSON
    try:
        result_json = json.loads(response.output_text)
        return jsonify(result_json)
    except Exception as e:
        app.logger.error(f"JSON 解析失败: {e}, 原始输出: {response.output_text}")
        return (
            jsonify({"error": "AI输出不是标准JSON", "raw": response.output_text}),
            500,
        )


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


@app.route("/analysis/test", methods=["GET"])
def analyze_test():
    result_json = {"孕囊大小": 52, "胚芽长": 11, "是否停育": False, "日期": "2025-03-27"}
    return jsonify(result_json)


@app.route("/analysis/test2", methods=["GET"])
def analyze_test2():
    result_json = {"孕囊大小": 24, "胚芽长": 9, "是否停育": True, "日期": "2025-01-10"}
    return jsonify(result_json)


@app.route("/analysis/test3", methods=["GET"])
def analyze_test3():
    result_json = {"孕囊大小": 25, "胚芽长": 4, "是否停育": False, "日期": ""}
    return jsonify(result_json)


@app.route("/analysis/test4", methods=["GET"])
def analyze_test4():
    result_json = {"孕囊大小": 25, "胚芽长": 4, "是否停育": False, "日期": "2025-01-01"}
    return jsonify(result_json)


@app.route("/analysis/test5", methods=["GET"])
def analyze_test5():
    result_json = {"孕囊大小": 24, "胚芽长": 9, "是否停育": True, "日期": ""}
    return jsonify(result_json)


@app.route("/analysis/test6", methods=["GET"])
def analyze_test6():
    result_json = {"孕囊大小": 12, "胚芽长": 0, "是否停育": False, "日期": ""}
    return jsonify(result_json)


if __name__ == "__main__":
    # # cd /root/Code/venv_313
    # # source bin/activate
    # # cd /root/Code/Hun_RESTful
    # # python 1_miscarry_calc.py
    # # decrypt.py 关30行开31行

    # # 打印所有注册的路由
    # for rule in app.url_map.iter_rules():
    #     print(f"{rule.endpoint}: {rule.rule} {rule.methods}")
    app.run(debug=True, port=5003)

    # app.run(debug=False, port=5003)
