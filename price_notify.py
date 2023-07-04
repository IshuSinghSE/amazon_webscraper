import os
import smtplib
from dotenv import load_dotenv
from jinja2 import Environment 
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from pathlib import Path
load_dotenv()

def shorter(name, index=10):
    shorted = ''
    for word in name[:index]:
        shorted += word + ' '
    return shorted
        
def notify(Subject="Some of product are on discount !!!", body="Dear Ishu! Check out the excel list now !"):
    try:
        sender_email =  os.getenv("USER_EMAIL") 
        passcode = os.getenv("USER_PASSWORD")    # add passcode here
        receiver_email = os.getenv("EMAIL")  # add email email here

        message = MIMEMultipart("alternative")
        message["Subject"] = Subject
        message["From"] = sender_email
        message["To"] = receiver_email

        # Create the plain-text and HTML version of your message
        link = body[0]
        name = shorter(body[1].split(),5)
        image = body[2]
        price = body[3]
        print(name)
        # Turn these into plain/html MIMEText objects
        report_file = open(Path("index.html"))
        template = MIMEText(Environment().from_string(report_file.read()).render(NAME=name,LINK=link,IMAGE=image,PRICE=price,EMAIL=sender_email), "html")
        message.attach(template)
        try:
            for i in range(1,5):
                img = ('image-'+str(i)+'.png')
                i = str(i)
                with open('./images/'+img, 'rb') as f:
                    # set attachment mime and file name, the image type is png
                    mime = MIMEBase('image', 'png', filename=img)
                    # add required header data:
                    mime.add_header('Content-Disposition', 'attachment', filename=img)
                    mime.add_header('X-Attachment-Id', i )
                    mime.add_header('Content-ID', '<'+i+'>')
                    # read attachment file content into the MIMEBase object
                    mime.set_payload(f.read())
                    # encode with base64
                    encoders.encode_base64(mime)
                    # add MIMEBase object to MIMEMultipart object
                    message.attach(mime)
        except Exception as e:
            print('Unable to fetch images !',e)

        try:
                conn = smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465) 
                conn.login(sender_email, passcode)
                conn.sendmail(sender_email,receiver_email,  message.as_string())
                conn.quit()
                print('Email sent <3')
                
        except Exception as e:
                print('- Yahoo did not responded as expected !\n', e)
        
    except Exception as e:
        print(" - Unable to fetch Email or Password\n", e)
               

# HTML = '''\
# <html>
# <body>
#     <p>Bonjour Ashu ❤!,<br>
#     Here is a discount on favourite product!<br>
#     <img src="{{image}}" alt="{{name}}"> <br>
#     <a href="{{link}} " style="text-decoration:none;">{{name}}</a> <br>
#     I am always here for you...💗
#     </p>
# </body>
# </html>
# '''