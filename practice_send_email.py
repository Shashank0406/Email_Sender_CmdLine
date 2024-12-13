import argparse
import smtplib
import sys
import getpass
import json
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

#setting up logger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s -%(message)s',
    filename='email_sender.log',  # File to write logs to
    filemode='a'
)
logger = logging.getLogger(__name__)

class EmailSender():
    def __init__(self):
        self.config = {}
        self.config_file = Path.home()/'.emailsender.json'
        self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    self.config = json.load(f)
                logger.info("Configured successfully")
            
            except json.JSONDecodeError:
                logger.info("Error loading config_file")
                self.config = {}
    
    def save_config(self):
        #saving congig file
        with open(self.config_file,'w') as f:
            json.dump(self.config,f)
        
        logger.info("save success")
    
    def setup_smtp(self):
        if not self.config:
            print("\First time Setup: Enter your SMTP Details:")
            self.config['smtp_server'] = input("SMTP server (eg:smtp@gmail.com)")
            self.config['smtp_port'] = input("SMTP PORT(587)")
            self.config['email']=input("enter your email")
            save = input("Save these setting for future use? y/n").lower()=='y'

            if save:
                self.save_config()
    
    def send_email(self,recipient,subject,body,password=None):

        if not password:
            password = getpass.getpass("Enter password")

        msg = MIMEMultipart()
        msg['From']=self.config['email']
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body,'plain'))

        try:
            with smtplib.SMTP(self.config['smtp_server'],int(self.config['smtp_port'])) as server:
                server.starttls()
                server.login(self.config['email'],password)
                server.send_message(msg)
                logger.info("Sent success")
                return True
        except Exception as e:
            logger.error(f"Failed to send email:{str(e)}")
            return False
def main():
    parser = argparse.ArgumentParser(description="cmd email sender")
    parser.add_argument('-t','--to',required=True,help='address')
    parser.add_argument('-s','--subject',required=True,help='subject')
    parser.add_argument('-b','--body',required=True,help=' body')
    parser.add_argument('--setup',action='store_true',help='run setup again')
    

    args = parser.parse_args()

    sender = EmailSender()

    if args.setup or not sender.config:
        sender.setup_smtp()

    
    if sender.send_email(args.to, args.subject, args.body):
        sys.exit(0)
    else:
        sys.exit(1)
    

if __name__ == "__main__":
    main()