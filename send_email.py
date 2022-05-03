import os
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
from config import app

def generate_email_body(recipient):
    email_body = f"""
    <html>
        <head></head>
        <body>
            <p>Dear {recipient},</p>

            <p>
            You can find the photo you took at <b>its.snaplab</b> attached. We also included the gif version of your photos!
            </p>

            <p>
            Thank you for using our services!
            </p>
            
            <p>
            <b>its.snaplab</b>
            </p>
        </body>
    </html>
    """
    return email_body

def compose_email(recipient_name, email, tx_id, effect):
    msg = MIMEMultipart('alternative')
    msg['From'] = app.config['EMAIL_USERNAME']
    msg['To'] = COMMASPACE.join(email)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = f"ITS.SNAPLAB - Photos for {recipient_name}"
    message_body = generate_email_body(recipient_name)

    results_dir = os.path.join(app.config["IMG_RESULT_BASE_DIR"], tx_id)
    attached_files = [
        os.path.join(results_dir, effect)+'/compiled.jpg',
        os.path.join(results_dir, effect)+'/compiled.gif'
    ]

    msg.attach(MIMEText(message_body, 'html'))
    for path in attached_files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename={}'.format(Path(path).name))
        msg.attach(part)
    
    return msg

def send_email(message, recipient_email, smtp_servername, smtp_serverport):
    smtp = smtplib.SMTP_SSL(smtp_servername, smtp_serverport)
    smtp.login(app.config['EMAIL_USERNAME'], app.config['EMAIL_PASSWD'])
    smtp.sendmail(app.config['EMAIL_USERNAME'], recipient_email, message.as_string())
    smtp.quit()