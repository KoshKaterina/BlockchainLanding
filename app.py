import os
import json
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, send_from_directory, request, jsonify
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__, static_folder='static')

SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID', '1qtBamkb8ZbCTpvUnF3PRsbNDHb972Xts62G7WOzJjBc')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def get_sheet():
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if not creds_json:
        raise RuntimeError('GOOGLE_CREDENTIALS env var not set')
    creds_info = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    gc = gspread.authorize(creds)
    return gc.open_by_key(SPREADSHEET_ID).sheet1


@app.route('/')
def index():
    return send_from_directory('static', 'sunscrypt_landing_v3.html')


@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


@app.route('/api/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json(force=True)

        name = (data.get('name') or '').strip()
        phone = (data.get('phone') or '').strip()
        contact = (data.get('contact') or '').strip()
        comment = (data.get('comment') or '').strip()
        tags = data.get('tags', [])

        if not phone or not contact:
            return jsonify({'status': 'error', 'message': 'phone and contact are required'}), 400

        if isinstance(tags, list):
            tags_str = ', '.join(tags)
        else:
            tags_str = str(tags)

        now = datetime.now().strftime('%d.%m.%Y %H:%M')

        sheet = get_sheet()
        sheet.append_row([now, name, phone, contact, comment, tags_str])

        return jsonify({'status': 'ok'})

    except Exception as e:
        app.logger.error(f'Submit error: {e}')
        return jsonify({'status': 'error', 'message': 'server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
