# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

msg = MIMEText('I need you to tell me if anaything is wrong with this email.')
# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = 'NICK this is a test 1 - amir'
msg['From'] = 'amir@aelsi.net'
msg['To'] = 'WHATEVER@NICKEU.COM'

# Send the message via our own SMTP server.
s = smtplib.SMTP('mail.aelsi.net', 587)
s.starttls()
s.login('amir@aelsi.net', 'Rock24!7')
s.send_message(msg)
s.quit()