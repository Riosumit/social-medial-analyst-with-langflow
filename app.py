from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import os, json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"]
)

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "e2a3dfca-7466-442e-ada7-fe7dd2446d3b"
FLOW_ID = "882824c5-c6a3-45dd-a45c-2d8051e446fd"
API_TOKEN = os.getenv("API_TOKEN")

@app.route("/process", methods=["POST"])
def process_text():
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({"error": "Invalid request, JSON data missing"}), 400

        user_input = request_data.get("text")
        if not user_input:
            return jsonify({"error": "Input text is required"}), 400

        endpoint_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{FLOW_ID}"
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "input_value": user_input,
            "input_type": "chat",
            "output_type": "chat",
        }

        api_response = requests.post(endpoint_url, json=payload, headers=headers)
        api_response.raise_for_status()
        langflow_response = api_response.json()
        message = langflow_response["outputs"][0]["outputs"][0]["results"]["message"]["data"]["text"]
        trimmed_message = message.lstrip("```json").rstrip("```\n").rstrip("```")
        message_json = json.loads(trimmed_message)
        return jsonify({"message": message_json})

    except requests.exceptions.RequestException as api_error:
        return jsonify({"error": f"LangFlow API error: {str(api_error)}"}), 500
    except Exception as general_error:
        return jsonify({"error": f"Unexpected server error: {str(general_error)}"}), 500


if __name__ == "__main__":
    app.run(debug=False)
