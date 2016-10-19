import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

subject = "Test html/link"
from_addr = "amir@aelsi.net"
dest_addr = "amir.elsibaie@gmail.com"

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = from_addr
msg['To'] = dest_addr

# Create the body of the message (a plain-text and an HTML version).
text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttps://www.python.org"
html = """\
<html>
  <head></head>
  <body>
    <p>Hi!<br>
       How are you?<br>
       Here is the <a href="https://www.python.org">link</a> you wanted.
    </p>
  </body>
</html>
"""

# Record the MIME types of both parts - text/plain and text/html.
part1_text = MIMEText(text, 'plain')
part2_html = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1_text)
msg.attach(part2_html)

# Send the message via our own SMTP server.
server = smtplib.SMTP('mail.aelsi.net', 587)

# Start TLS connection and login
server.starttls()
server.login('amir@aelsi.net', 'Rock24!7')

# sendmail function takes 3 arguments: sender's address, recipient's address
# and message to send - here it is sent as one string.
server.sendmail(from_addr, dest_addr, msg.as_string())
server.quit()