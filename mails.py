from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP


from utils import parse_config
def api_email(api_title, headers=None, html=None, fail=None):
    """
    email sending in case api is down
    """
    msg = MIMEMultipart()
    attach_txt = txt = ''
    mail = parse_config(mails=True)

    if html:
        #attach html dump
        content = MIMEApplication(html)
        content.add_header('Content-Disposition', 'attachment', filename=api_title.lower()+'_content.html')
        msg.attach(content)

    if headers:
        #attach header dump
        head = MIMEApplication(headers)
        head.add_header('Content-Disposition', 'attachment', filename=api_title.lower()+'_headers.html')
        msg.attach(head)


    if fail:
        msg['Subject'] = "API headers test failed for %s \n" % api_title
        txt += "*** A gentle prod to remind you ***\n"
        txt += """ %s API seems to be down.
        Fabricbot tried to crawl the api response but no valid content was retreived.
        Also, invalid http headers were received from server.

        --
        The site monitoring automation""" % api_title
    else:
        msg['Subject'] = "API content test failed for %s \n" % api_title
        txt += "*** A gentle prod to remind you ***\n"
        txt += """ %s API seems to be down.
        Fabricbot tried to crawl the api response but no valid content was retreived.

        --
        The site monitoring automation""" % api_title



    msg['From'] = 'fabricapi'
    msg['To'] = mail[1]

    # That is what u see if dont have an email reader:
    msg.preamble = 'Multipart massage.\n'

    # This is the textual part:
    part = MIMEText(txt)
    msg.attach(part)

    # Create an instance in SMTP server
    smtp = SMTP('localhost')
    # Send the email
    smtp.sendmail(msg['From'], msg['To'], msg.as_string())
    smtp.quit()

def site_email(hostnames, failed_urls, content, status_code, status=None, rerun=None):
    msg = MIMEMultipart()
    attach_txt = txt = ''
    failed = []

    #merge url and status_code lists in one list
    for x, y in zip(failed_urls, status_code):
        failed.append(x+"   |   response code: "+str(y))
    failed = ', \n\t'.join(failed)
    mail = parse_config(mails=True)

    if 200 in status_code:
        attach_txt = "Even though it is a valid response code, errors were detected in what was rendered. Please inspect the attached file."
        #prepare html and attach it to mail message
        for (hostname, html) in zip(hostnames, content):
            part = MIMEApplication(html)
            part.add_header('Content-Disposition', 'attachment', filename=hostname.lower()+'.html')
            msg.attach(part)

    #send mail for the first two passes
    if status:
        if not rerun:
            msg['Subject'] = "NOTICE: The following web hosts seems to be down\n"
            txt += "*** A gentle prod to remind you ***\n"
            txt += """
        It has been detected that the following hosts are down.
        %s

        hostnames and response codes: \n:
        %s

        Fabricbot tried to clear the cache tables.
        If you do not receive any more mails, that means that the problem is gone.

        --
        The site monitoring automation""" % (attach_txt, failed)

        else:
            msg['Subject'] = "NOTICE: The following web hosts seems to be down\n"
            txt += "*** A gentle prod to remind you ***\n"
            txt += """
        Again, it has been detected that the following hosts are down.
        %s

        hostnames and response codes: \n:
        %s

        Fabricbot tried to clear APC cache.
        If you do not receive any more mails, that means that the problem is gone.

        --
        The site monitoring automation""" % (attach_txt, failed)

    #send mail for the third pass
    #bot hasn't succeded to fix the problem
    else:
            msg['Subject'] =  "WARNING: Apache server not reponding!!!\n"
            txt += "*** A gentle prod to remind you ***\n"
            txt += """
        As you already know, it has been multiple times detected that the following hosts are down.
        %s

        hostnames and response codes: \n:
        %s

        Fabricbot tried to clear the drupal cache tables and APC cache. That didn't work.

        Please log on to servers, check the logs and fix the problem manualy ASAP!!!

        --
        The site monitoring automation""" % (attach_txt, failed)


    msg['From'] = 'fabricbot'
    msg['To'] = mail[1]

    # That is what u see if dont have an email reader:
    msg.preamble = 'Multipart massage.\n'

    # This is the textual part:
    part = MIMEText(txt)
    msg.attach(part)

    # Create an instance in SMTP server
    smtp = SMTP('localhost')
    # Send the email
    smtp.sendmail(msg['From'], msg['To'], msg.as_string())
    smtp.quit()
