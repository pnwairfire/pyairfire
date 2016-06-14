"""pyairfire.statuslogging.statusnotifier

TODO:
 - use templating system for html (and text?) email
 - add option to pass in custom status log html/text formatter
"""

__author__      = "Joel Dubowy"

import json
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .statusreader import StatusReader


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

    def __init__(self, api_endpoint, **options):
        """Constructor

        Arguments:
         - api_endpoint

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
        self.status_reader = StatusReader(api_endpoint)

    def query_and_notify(self, query=None, subject=None):
        # query
        query = query or {}
        logs = self.status_reader.read(**query)

        # notify
        self.send(logs, subject=subject, query=query)

        return logs

    def send(self, status_logs, subject=None, query=None):
        for channel in ['email', 'sms']:
            try:
                m = getattr(self, 'send_%s' % (channel))
                m(status_logs, subject=subject, query=query)

            except StatusNotificationError as e:
                # log message but move on
                logging.error("Failed to send %s: %s", channel, e)

    ## Email

    DEFAULT_EMAIL_SENDER = "bluesky-status@airfire.org"
    DEFAULT_EMAIL_SUBJECT = "Status Log Digest"
    DEFAULT_MAIL_SERVER = "localhost"
    def send_email(self, status_logs, subject=None, query=None,
            email_content_generator=None):
        """
        Note: email_content_generator is intended for clients calling this method
          directly
        """
        recipients = self.options.get('email_recipients')
        if not recipients:
            return

        sender = self.options.get('email_sender')
        logging.info('Sending Email to %s', recipients)
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = sender or self.DEFAULT_EMAIL_SENDER
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject or self.DEFAULT_EMAIL_SUBJECT

            content = (email_content_generator(status_logs, query=query)
                if email_content_generator
                else self.generate_email_content(status_logs, query=query))

            msg.attach(MIMEText(content['text'], 'plain'))
            msg.attach(MIMEText(content['html'], 'html'))

            server = self.options.get('smtp_server') or self.DEFAULT_MAIL_SERVER
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

        except smtplib.SMTPException as e:
            # Note: e's message is blank
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
            ''.join(['<li><span class="key">%s</span>: %s</li>' % (k, v) for (k, v) in list(query.items())]) if query else "",
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
                ''.join(['<li><span class="key">%s</span>: %s</li>' % (k, v) for (k, v) in list(status_log.items())]),
            )
        else:
            html = """
                <div>
                    <span class="%s">%s</span> - %s - %s - %s - %s - %s...
                </div>
            """ % (
                status_log['status'].lower(),
                status_log['status'],
                status_log['process'],
                status_log.get('domain'),
                status_log.get('initialization_time'),
                status_log.get('machine'),
                status_log.get('notes', '')[:40]
            )

        return html

    ## SMS

    DEFAULT_SMS_SENDER = "" # TODO: Fill this in
    def send_sms(self, status_logs, subject=None, query=None):
        recipients = self.options.get('sms_recipients')
        if not recipients:
            return

        sender = self.options.get('sms_sender')
        logging.debug('Sending SMS')
        # TODO: send sms to all addressses in to_email
        raise StatusSMSError("SMS not supported")
