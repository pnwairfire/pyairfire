"""pyairfire.statuslogging.statusnotifier

TODO:
 - use templating system for html (and text?) email
 - add option to pass in custom status log html/text formatter
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import json
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from statusreader import StatusReader


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
         - smtp_server --
         - smtp_starttls --
         - smtp_username --
         - smtp_password --
        """
        self.options = options

    def query_and_notify(self, api_endpoint, query=None, subject=None):
        # query
        sr = StatusReader(api_endpoint)
        query = query or {}
        logs = sr.read(**query)

        # notify
        self.send(logs, subject=subject, query=query)

        return logs

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

            server = self.options.get('smtp_server') or self.DEFAILT_MAIL_SERVER
            logging.debug('Connecting to SMTP server %s', server)
            s = smtplib.SMTP(server)

            if self.options.get('smtp_starttls'):
                logging.debug('Using STARTTLS')
                s.ehlo()
                s.starttls()
                s.ehlo()

            if self.options.get('smtp_username') and self.options.get('smtp_password'):
                logging.debug('Logging into SMTP server with u/p')
                s.login(self.options['smtp_username'], self.options['smtp_password'])

            s.sendmail(msg['from'], recipients, msg.as_string())
            s.quit()

        except smtplib.SMTPException, e:
            # Note: e.message is blank
            raise StatusNotificationError(str(e))

    def generate_email_content(self, status_logs, query=None):
        text = json.dumps(status_logs)
        logging.debug("Email contents (text):\n%s", text)

        html = """
            <html>
              <head>
                <style type="text/css">
                  .failure {
                    color: red;
                  }
                  .good {
                    color: green;
                  }
                  li span.key {
                      font-weight: bold;
                  }
                </style>
              </head>
              <body>
                <div>
                    <h2>Query</h2>
                    <ul>
                        %s
                    </ul>
                </div>
                <div>
                    <h2>%d Matching Statuses Logs Found</h2>
                    %s
                </div>
                <div>
                    <h2>Details</h2>
                    %s
                </div>
              </body>
            </html>
        """ % (
            ''.join(['<li><span class="key">%s</span>: %s</li>' % (k, v) for (k, v) in query.items()]) if query else "",
            len(status_logs['logs']),
            ''.join([self.status_log_as_html(sl, verbose=False) for sl in status_logs['logs']]),
            ''.join([self.status_log_as_html(sl) for sl in status_logs['logs']])
            )
        logging.debug("Email contents (html):\n%s", html)

        # TODO: strip leading/trailing whitespace from html, and then remove newlines
        return {
            'text': text,
            'html': html
        }

    def status_log_as_html(self, status_log, verbose=True):
        if verbose:
            html = """
                <div>
                    <div>Process: %s</div>
                    <div>Status: <span class="%s">%s<span></div>
                    <ul>
                        %s
                    </ul>
                </div>
            """ % (
                status_log['process'],
                status_log['status'].lower(),
                status_log['status'],
                ''.join(['<li><span class="key">%s</span>: %s</li>' % (k, v) for (k, v) in status_log.items()]),
            )
        else:
            html = """
                <div>
                    %s - %s - <span class="%s">%s</span> - %s - %s
                </div>
            """ % (
                status_log['process'],
                status_log.get('domain'),
                status_log['status'].lower(),
                status_log['status'],
                status_log.get('initialization_time'),
                status_log.get('machine'),
            )

        return html

    ## SMS

    DEFAULT_SMS_SENDER = "" # TODO: Fill this in
    def send_sms(self, status_logs, recipients, sender=None, subject=None, query=None):
        logging.debug('Sending SMS')
        # TODO: send sms to all addressses in to_email
        raise StatusSMSError("SMS not supported")
