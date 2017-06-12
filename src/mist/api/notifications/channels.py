
from mist.api import config


class BaseChannel():
    '''
    Represents a notification channel
    '''

    def send(self, notification):
        '''
        Accepts a notification and sends it using the
        current channel instance.
        '''
        pass


class EmailReportsChannel(BaseChannel):
    '''
    Email channel for reports.
    Tries to send using Sendgrid, if credentials are available
    in config, otherwise sends email using SMTP.
    '''

    def send(self, notification):
        '''
        Accepts a notification and sends an email using included data.
        If SENDGRID_REPORTING_KEY and EMAIL_REPORT_SENDER are available
        in config, it uses Sendgrid to deliver the email. Otherwise, it
        uses plain SMTP through send_email()
        '''
        user = notification["user"]

        to = notification.get("email", user.email)
        full_name = notification.get("full_name", user.get_nice_name())
        first_name = notification.get(
                "name", user.first_name or user.get_nice_name())

        if (hasattr(config, "SENDGRID_REPORTING_KEY") and
            hasattr(config, "EMAIL_REPORT_SENDER")):
            from sendgrid.helpers.mail import (Email,
                                   Mail,
                                   Personalization,
                                   Content,
                                   Substitution)
            import sendgrid

            self.sg_instance = sendgrid.SendGridAPIClient(
                apikey=config.SENDGRID_REPORTING_KEY)

            mail = Mail()
            mail.from_email = Email(config.EMAIL_REPORT_SENDER, "Mist.io Reports")
            personalization = Personalization()
            personalization.add_to(Email(to, full_name))
            personalization.subject = notification["subject"]
            sub1 = Substitution("%name%", first_name)
            personalization.add_substitution(sub1)
            if "unsub_link" in notification:
                sub2 = Substitution("%nsub%", notification["unsub_link"])
                personalization.add_substitution(sub2)
            mail.add_personalization(personalization)

            mail.add_content(Content("text/plain", notification["body"]))
            if "html_body" in notification:
                mail.add_content(Content("text/html", notification["html_body"]))

            mdict = mail.get()
            try:
                return self.sg_instance.client.mail.send.post(request_body=mdict)
            except Exception as exc:
                print str(exc)
                print exc.read()
        else:
            send_email(subject, notification["body"], 
                [to], sender="config.EMAIL_REPORT_SENDER")


class StdoutChannel(BaseChannel):
    '''
    Stdout channel, mainly for testing/debugging
    '''

    def send(self, notification):
        print notification["subject"]
        if "summary" in notification:
            print notification["summary"]
        print notification["body"]


def channel_instance_with_name(name):
    '''
    Accepts a string and returns a channel instance with
    matching name or None
    '''
    if name == 'stdout':
        return StdoutChannel()
    elif name == 'email_reports':
        return EmailReportsChannel()
    return None
