import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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

