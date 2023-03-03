import smtplib
import imghdr
from email.message import EmailMessage

password = "password"
email = "email"


def send_email(img_path):
    email_message = EmailMessage()
    email_message["Subject"] = "Motion in Camera!"
    email_message.set_content("A foreign object was spotted in the frame.")

    with open(img_path, "rb") as file:
        content = file.read()

    email_message.add_attachment(content, maintype="image", subtype=imghdr.what(None, content))

    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(email, password)
    gmail.sendmail(email, email, email_message.as_string())
    gmail.quit()


if __name__ == '__main__':
    send_email("images/1.png")