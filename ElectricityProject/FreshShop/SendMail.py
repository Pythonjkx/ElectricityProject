import smtplib #登陆邮件服务器，进行邮件发送
from email.mime.text import MIMEText #负责构建邮件格式

subject = "在线征婚！！！"
content = "张鹏，男，177，男女不限，欢迎大家投稿！！！"
sender = "329688391@qq.com"
recver = """215558997@qq.com,
773733859@qq.com,
912575770@qq.com,
1529825704@qq.com,
1307128051@qq.com,
721788741@qq.com,
3303236612@qq.com,
710731910@qq.com,
626978318@qq.com,
419538402@qq.com,
1637805820@qq.com,
738389368@qq.com,
515352258@qq.com,
1195531526@qq.com,
215558997@qq.com,
1270667973@qq.com,
793115964@qq.com,
1056940091@qq.com,
385726424@qq.com,
1225858108@qq.com,
1529825704@qq.com,
1225858108@qq.com"""

password = "tavbbiyhphoncaaj"

message = MIMEText(content,"plain","utf-8")
message["Subject"] = subject
message["To"] = recver
message["From"] = sender

smtp = smtplib.SMTP_SSL("smtp.qq.com",465)
smtp.login(sender,password)
smtp.sendmail(sender,recver.split(",\n"),message.as_string())
smtp.close()






