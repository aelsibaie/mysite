# Import smtplib for the actual sending function
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Import the email modules we'll need
from email.mime.text import MIMEText

<<<<<<< HEAD
fromaddr = "amir@aelsi.net"
toaddr = "amir.elsibaie@gmail.com"

msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "validitity sdasdas2"
body = "Test of validitity "
msg.attach(MIMEText(body, 'plain'))

server = smtplib.SMTP('mail.aelsi.net', 587)
server.set_debuglevel(1)
server.starttls()
server.login(fromaddr, 'Rock24!7')

text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
=======
msg = MIMEText('I need you to tell me if anaything is wrong with this email.')
# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = 'NICK this is a test 1 - amir'
msg['From'] = 'amir@aelsi.net'
msg['To'] = 'WHATEVER@NICKEU.COM'
>>>>>>> origin/master

# Send the message via our own SMTP server.
s = smtplib.SMTP('mail.aelsi.net', 587)
s.starttls()
s.login('amir@aelsi.net', 'Rock24!7')
s.send_message(msg)
s.quit()