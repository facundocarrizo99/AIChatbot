import json
import logging
from app.services.openai_service import generate_ai_response
import re
import requests
from flask import current_app, jsonify

def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")

def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
            requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response

def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text

def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]

    # TODO: Replace phone number normalization with proper E.164 handling
    if wa_id.startswith("54911"):
        new_wa_id = wa_id.replace("54911", "5411")
    else:
        new_wa_id = wa_id

    response = generate_ai_response(message_body, new_wa_id, name)

    response = process_text_for_whatsapp(response)
    data = get_text_message_input(new_wa_id, response)
    send_message(data)

def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
            body.get("object")
            and body.get("entry")
            and body["entry"][0].get("changes")
            and body["entry"][0]["changes"][0].get("value")
            and body["entry"][0]["changes"][0]["value"].get("messages")
            and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )

def send_document_message(recipient_number, file_path, filename_to_display="documento.pdf"):
    # Step 1: Upload the PDF to Meta
    media_upload_url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/media"
    headers_auth = {
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    try:
        with open(file_path, 'rb') as pdf_file:
            files = {
                "file": (filename_to_display, pdf_file, "application/pdf")
            }
            data = {
                "messaging_product": "whatsapp"
            }
            upload_response = requests.post(media_upload_url, headers=headers_auth, files=files, data=data)
            upload_response.raise_for_status()

        media_id = upload_response.json().get("id")
        logging.info(f"Media uploaded: id={media_id}, filename={filename_to_display}")
        if not media_id:
            raise RuntimeError("No media_id received from server.")
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        return jsonify({"status": "error", "message": f"Error uploading file: {str(e)}"}), 500

    # Step 2: Send message with the media_id

    message_url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"
    headers_message = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_number,
        "type": "document",
        "document": {
            "id": media_id,
            "filename": filename_to_display
        },
        "recipient_type": "individual"
    }

    try:
        response = requests.post(message_url, json=payload, headers=headers_message, timeout=10)
        #response = send_message(payload)
        response.raise_for_status()
    except requests.Timeout:
        logging.error("Timeout sending PDF")
        return jsonify({"status": "error", "message": "Timeout sending PDF"}), 408
    except requests.RequestException as e:
        logging.error(f"Error sending document message: {e}")
        return jsonify({"status": "error", "message": "Failed to send PDF"}), 500
    else:
        logging.info("PDF sent successfully.")
        return jsonify({"status": "success", "response": response.json()}), 200
