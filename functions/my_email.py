# my_email.py

"""
    @author Christopher Pickering

    used to create email message for sending daily reports.
    will send with attachments or html body

"""

from functions.my_settings import subscriptions, email_settings
import time
from datetime import date
import calendar
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
import smtplib
import sys
from pathlib import Path
import jinja2
import json

class Email:
    
    def __init__(self,report,message):

        self.report_name = report.replace("_",' ').lower()
        self.subject = report.replace("_",' ') + " " + time.strftime("%d-%b-%y")
        self.file_location = Path(__file__).parents[1].joinpath('excel',report).with_suffix('.xlsx')

        # get today
        today = calendar.day_name[date.today().weekday()]

        # import templates
        templates = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(Path(__file__).parents[1] / 'templates')),trim_blocks=True)

        message_data = {'message':message,'today':today,'report_name':self.report_name}

        self.message = templates.get_template('report.html').render(message_data)
        
        # if testing or an error
        if Path(sys.argv[0]).stem == 'test' or self.report_name.endswith('error'):
            self.subscriptions = [x.strip() for x in subscriptions['ErrorAddress'].split(',')]
            self.recipients = subscriptions['ErrorAddress']
       
        # send normal emails
        else:
            self.subscriptions = [x.strip() for x in subscriptions[self.report_name].split(',')]
            self.recipients = subscriptions[self.report_name]          

    def SendMail(self):

        # creat message
        msg = MIMEMultipart()

        # email headers
        msg['Subject'] = self.subject
        msg['To'] =  self.recipients
        msg['From'] = email_settings['default_sender']
        msg['Reply-To'] = email_settings['reply_to']

        # email message
        msg.attach(MIMEText(self.message, 'html'))

        # add attachment
        if self.file_location.is_file():

            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(str(self.file_location), "rb").read())

            part.add_header('Content-Disposition', 'attachment; filename=' + self.subject.replace(' ','_') + '.xlsx')
            encoders.encode_base64(part)
            msg.attach(part)

        # add logo signature
        # for this to work the img src must be "cid:<image1>"
        fp = open(str(Path(__file__).parents[1].joinpath('templates','logo').with_suffix('.png')),'rb')
        msgImage = MIMEImage(fp.read())
        msgImage.add_header('Content-ID', '<image1>')
        msg.attach(msgImage)
        fp.close()

        # send mail
        server = smtplib.SMTP(email_settings['address'],timeout=10)
        server.ehlo()
        server.sendmail(msg['From'], self.subscriptions, msg.as_string())
        server.close()
