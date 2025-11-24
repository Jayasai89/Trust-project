from flask import Flask, render_template, request, jsonify
import pyodbc
import os
from dotenv import load_dotenv
import requests  # Uncomment when you integrate real UPI Collect API

load_dotenv()

app = Flask(__name__)

driver = os.getenv('SQL_SERVER_DRIVER')
server = os.getenv('SQL_SERVER_HOST')
database = os.getenv('SQL_SERVER_DB')
auth = os.getenv('SQL_SERVER_AUTH')
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'{auth};'
)


# Example UPI Collect request (pseudo, not active)
# Replace with real payment gateway API details if using Setu/Juspay/Razorpay/PayU etc.
def send_upi_collect(customer_vpa, amount, note="Contribution for trust"):
    
    url = "https://api.paymentgateway.com/upi-collect"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    payload = {
        "customer_vpa": customer_vpa,
        "merchant_vpa": "yourtrust@bank",
        "amount": str(amount),
        "reference_id": "TXN" + customer_vpa[-6:],
        "note": note
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
    return {"info": "UPI collect not active (add API details to enable)."}

# 🏠 Dashboard
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# 💰 Give Help (form page)
@app.route('/givehelp')
def give_help():
    return render_template('give_help.html')

# 🙌 Get Help intro page
@app.route('/gethelp')
def get_help():
    return render_template('get_help.html')

@app.route('/gethelpform')
def gethelpform():
    return render_template('gethelpform.html')

# ✅ Give Help submission, now with UPI fields
@app.route('/submit', methods=['POST'])
def submit_give_help():
    try:
        data = request.get_json()
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute('''
    INSERT INTO GiveHelp
    (name, email, phone, org, amount, type, school, frequency, interest, volunteer, skills,
     referral, message, agree, contribution_method, upi_id, upi_amount,
     update_channel, whatsapp_updates, email_updates, contribution_purpose)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    data.get('name'),
    data.get('email'),
    data.get('phone'),
    data.get('org'),
    data.get('amount'),
    ', '.join(data.get('type', [])) if isinstance(data.get('type'), list) else data.get('type'),
    data.get('school'),
    data.get('frequency'),
    data.get('interest'),
    data.get('volunteer'),
    data.get('skills'),
    ', '.join(data.get('referral', [])) if isinstance(data.get('referral'), list) else data.get('referral'),
    data.get('message'),
    data.get('agree'),
    data.get('contribution_method'),
    data.get('upi_id'),
    data.get('upi_amount'),
    ', '.join(data.get('update_channel', [])) if isinstance(data.get('update_channel'), list) else data.get('update_channel'),
    data.get('whatsapp_updates'),
    data.get('email_updates'),
    data.get('contribution_purpose')
))

        conn.commit()
        conn.close()

        # Trigger UPI collect request (pseudo, not active)
        if data.get('contribution_method') == 'UPI' and data.get('upi_id') and data.get('upi_amount'):
            upi_response = send_upi_collect(data['upi_id'], data['upi_amount'], "Trust Contribution")
            print(upi_response)

        return jsonify({"redirect": "/submitted"})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

# ✅ Get Help submission
@app.route('/submit-beneficiary', methods=['POST'])
def submit_get_help():
    try:
        data = request.get_json()
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO GetHelp
            (full_name, dob, gender, class_grade, school_name, mobile, email, address, guardian_name,
             guardian_contact, family_income, reason, contact_mode, comments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('full_name'),
            data.get('dob'),
            data.get('gender'),
            data.get('class_grade'),
            data.get('school_name'),
            data.get('mobile'),
            data.get('email'),
            data.get('address'),
            data.get('guardian_name'),
            data.get('guardian_contact'),
            data.get('family_income'),
            data.get('reason'),
            data.get('contact_mode'),
            data.get('comments')
        ))
        conn.commit()
        conn.close()
        return jsonify({"redirect": "/submitted"})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/submitted')
def submitted():
    return render_template('submitted.html')

if __name__ == '__main__':
    app.run(debug=True)
