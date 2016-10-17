import smtplib


fromaddr = "pi@aelsi.ddns.us"
toaddrs = "amir.elsibaie@gmail.com"
msg = "test_123"

server = smtplib.SMTP('192.168.1.14', 587)
server.set_debuglevel(1)
server.starttls()

#server.login('raspberry', '')

server.sendmail(fromaddr, toaddrs, msg)

