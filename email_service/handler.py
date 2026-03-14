import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_FROM = os.environ.get('EMAIL_FROM', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')


def send_email(to_email, subject, html_body):
    """Send an HTML email via Gmail SMTP SSL."""
    msg = MIMEMultipart('alternative')
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
    print(f"[EMAIL] Sent '{subject}' to {to_email}")


def send_notification(event, context):
    """
    AWS Lambda / serverless-offline handler.
    Accepts POST requests with a JSON body.

    Supported actions:
    - SIGNUP_WELCOME
    - BOOKING_CONFIRMATION
    """
    try:
        # Parse request body
        raw_body = event.get('body', '{}')
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        action = body.get('action')

        if not action:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required field: action'})
            }

        # ---- SIGNUP_WELCOME ----
        if action == 'SIGNUP_WELCOME':
            name = body.get('name', 'User')
            email = body.get('email')
            if not email:
                return {'statusCode': 400, 'body': json.dumps({'error': 'Missing email'})}

            subject = 'Welcome to HMS! 🏥'
            html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 560px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #1a73e8, #0d47a1); padding: 32px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">🏥 Welcome to HMS</h1>
                </div>
                <div style="padding: 32px; background: #fff; border: 1px solid #e0e0e0; border-radius: 0 0 8px 8px;">
                    <h2 style="color: #333;">Hi {name}! 👋</h2>
                    <p style="color: #555; line-height: 1.6;">
                        Your account on the <strong>Hospital Management System</strong> has been created successfully.
                    </p>
                    <p style="color: #555; line-height: 1.6;">
                        You can now log in and start using the system to manage appointments.
                    </p>
                    <div style="text-align: center; margin-top: 28px;">
                        <a href="http://127.0.0.1:8000/accounts/login/"
                           style="background: #1a73e8; color: white; padding: 12px 28px;
                                  border-radius: 6px; text-decoration: none; font-weight: 600;">
                            Login to HMS
                        </a>
                    </div>
                </div>
                <p style="text-align:center; color:#aaa; font-size:12px; margin-top:16px;">
                    Hospital Management System &mdash; Demo Project
                </p>
            </div>
            """
            send_email(email, subject, html)

        # ---- BOOKING_CONFIRMATION ----
        elif action == 'BOOKING_CONFIRMATION':
            patient_email = body.get('patient_email')
            doctor_email = body.get('doctor_email')
            patient_name = body.get('patient_name', 'Patient')
            doctor_name = body.get('doctor_name', 'Doctor')
            date = body.get('date', '')
            start_time = body.get('start_time', '')
            end_time = body.get('end_time', '')

            if not patient_email or not doctor_email:
                return {'statusCode': 400, 'body': json.dumps({'error': 'Missing email addresses'})}

            # Email to Patient
            patient_html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 560px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #2e7d32, #1b5e20); padding: 32px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">✅ Appointment Confirmed</h1>
                </div>
                <div style="padding: 32px; background: #fff; border: 1px solid #e0e0e0; border-radius: 0 0 8px 8px;">
                    <p style="color: #555;">Hi <strong>{patient_name}</strong>,</p>
                    <p style="color: #555; line-height: 1.6;">Your appointment has been <strong>confirmed</strong>!</p>
                    <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0; border-left: 4px solid #1a73e8;">
                        <p style="margin:0 0 8px;"><strong>Doctor:</strong> Dr. {doctor_name}</p>
                        <p style="margin:0 0 8px;"><strong>Date:</strong> {date}</p>
                        <p style="margin:0;"><strong>Time:</strong> {start_time} – {end_time}</p>
                    </div>
                    <p style="color: #888; font-size: 13px;">
                        📅 A Google Calendar event has been created and an invite sent to your email.
                    </p>
                </div>
            </div>
            """

            # Email to Doctor
            doctor_html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 560px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #1a73e8, #0d47a1); padding: 32px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">📋 New Appointment</h1>
                </div>
                <div style="padding: 32px; background: #fff; border: 1px solid #e0e0e0; border-radius: 0 0 8px 8px;">
                    <p style="color: #555;">Hi <strong>Dr. {doctor_name}</strong>,</p>
                    <p style="color: #555; line-height: 1.6;">A new appointment has been booked with you.</p>
                    <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0; border-left: 4px solid #2e7d32;">
                        <p style="margin:0 0 8px;"><strong>Patient:</strong> {patient_name}</p>
                        <p style="margin:0 0 8px;"><strong>Date:</strong> {date}</p>
                        <p style="margin:0;"><strong>Time:</strong> {start_time} – {end_time}</p>
                    </div>
                    <p style="color: #888; font-size: 13px;">
                        📅 A Google Calendar invite has been sent to your email.
                    </p>
                </div>
            </div>
            """

            send_email(patient_email, 'Appointment Confirmed - HMS 🏥', patient_html)
            send_email(doctor_email, 'New Appointment Booked - HMS 🏥', doctor_html)

        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Unknown action: {action}'})
            }

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Email sent successfully', 'action': action})
        }

    except smtplib.SMTPAuthenticationError:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Email authentication failed. Check EMAIL_FROM and EMAIL_PASSWORD in .env'})
        }
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
