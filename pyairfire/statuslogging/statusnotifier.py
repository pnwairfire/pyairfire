"""pyairfire.statuslogging.statusnotifier
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import json
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

__all__ = [
    'StatusNotifier',
    'StatusEmailError'
]

class StatusNotificationError(Exception):
    pass
class StatusEmailError(StatusNotificationError):
    pass
class StatusSMSError(StatusNotificationError):
    pass

class StatusNotifier(object):
    """Class for querying the statuslog API
    """

    def __init__(self, **options):
        """Constructor

        Options:
         - email_recipients --
         - email_sender --
         - sms_recipients --
         - sms_sender --
        """
        self.options = options

    def send(self, status_logs, subject=None, query=None):
        for channel in ['email', 'sms']:
            recipient_key = '%s_recipients' % (channel)
            sender_key = '%s_sender' % (channel)
            if self.options.get(recipient_key):
                try:
                    m = getattr(self, 'send_%s' % (channel))
                    m(status_logs, self.options[recipient_key],
                        sender=self.options.get(sender_key), subject=subject, query=query)

                except StatusNotificationError, e:
                    # log message but move on
                    logging.error("Failed to send %s: %s", channel, e.message)

    ## Email

    DEFAULT_EMAIL_SENDER = "no-reply@status"
    DEFAULT_EMAIL_SUBJECT = "Status Log Digest"
    DEFAILT_MAIL_SERVER = "localhost"
    def send_email(self, status_logs, recipients, sender=None, subject=None, query=None):
        logging.debug('Sending Email')
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = sender or self.DEFAULT_EMAIL_SENDER
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject or self.DEFAULT_EMAIL_SUBJECT

            content = self.generate_email_content(status_logs, query=query)
            msg.attach(MIMEText(content['text'], 'plain'))
            msg.attach(MIMEText(content['html'], 'html'))

            s = smtplib.SMTP(self.options.get('smtp_server') or self.DEFAILT_MAIL_SERVER)
            s.ehlo()
            s.starttls()
            s.ehlo()

            if self.options.get('smtp_username') and self.options.get('smtp_password'):
                s.login(self.options['smtp_username'], self.options['smtp_password'])
            s.sendmail(msg['from'], msg['recipients'], msg.as_string())
            s.quit()
        except smtplib.SMTPException, e:
            # Note: e.message is blank
            raise StatusNotificationError(str(e))

    def generate_email_content(self, status_logs, query=None):
        html = """
            <html>
              <head></head>
              <body>
                %s
              </body>
            </html>
        """ % ('\n'.join([json.dumps(sl) for sl in status_logs]))  # TEMP

        return {
            'text': json.dumps(status_logs), # TEMP
            'html': html
        }

    ## SMS

    DEFAULT_SMS_SENDER = "" # TODO: Fill this in
    def send_sms(self, status_logs, recipients, sender=None, subject=None, query=None):
        logging.debug('Sending SMS')
        # TODO: send sms to all addressses in to_email
        raise StatusSMSError("SMS not supported")
