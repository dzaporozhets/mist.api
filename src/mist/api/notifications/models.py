from uuid import uuid4
from datetime import datetime

import mongoengine as me

from mist.api.users.models import User, Organization


class NotificationOverride(me.EmbeddedDocument):
    '''
    Represents a single notification override.
    '''
    source = me.StringField(max_length=64, required=True, default="")

    machine_id = me.StringField(max_length=128, required=False)
    tag_id = me.StringField(max_length=64, required=False)
    cloud_id = me.StringField(max_length=64, required=False)

    value = me.StringField(max_length=7, required=True,
                           choices=('ALLOW', 'BLOCK'), default='BLOCK')

    def matches_notification(self, notification):
        if self.machine_id and notification.machine:
            if self.machine_id != notification.machine.id:
                return False
        if self.tag_id and notification.tag:
            if self.tag_id != notification.tag.id:
                return False
        if self.cloud_id and notification.cloud:
            if self.cloud_id != notification.cloud.id:
                return False
        return self.source == type(notification).__name__


class UserNotificationPolicy(me.Document):
    '''
    Represents a notification policy associated with a
    user-organization pair, and containing a list of rules.
    '''
    rules = me.EmbeddedDocumentListField(NotificationOverride)
    user = me.ReferenceField(User, required=True)
    organization = me.ReferenceField(Organization, required=True)

    def notification_allowed(self, notification, default=True):
        '''
        Accepts a notification and returns a boolean
        indicating whether corresponding notification is allowed
        or is blocked
        '''
        for rule in self.rules:
            if rule.matches_notification(notification):
                if rule.value == 'BLOCK':
                    return False
                elif rule.value == 'ALLOW':
                    return True
        return default

    def channel_allowed(self, channel, default=True):
        '''
        Accepts a string token and returns a boolean
        indicating whether corresponding notification is allowed
        or is blocked
        '''
        for rule in self.rules:
            if (rule.source == channel and
                    rule.value == 'BLOCK'):
                return False
            elif (rule.source == channel and
                    rule.value == 'ALLOW'):
                return True
        return default


class Notification(me.Document):
    '''
    Represents a notification associated with a
    user-organization pair
    '''
    meta = {'allow_inheritance': True}

    id = me.StringField(primary_key=True,
                        default=lambda: uuid4().hex)

    created_date = me.DateTimeField(required=False)
    expiry_date = me.DateTimeField(required=False)

    user = me.ReferenceField(User, required=True)
    organization = me.ReferenceField(Organization, required=True)

    # content fields
    summary = me.StringField(max_length=512, required=False, default="")
    body = me.StringField(required=True, default="")
    html_body = me.StringField(required=False, default="")

    # taxonomy fields
    source = me.StringField(max_length=64, required=True, default="")
    machine = me.GenericReferenceField(required=False)
    tag = me.GenericReferenceField(required=False)
    cloud = me.GenericReferenceField(required=False)

    action_link = me.URLField(required=False)

    unique = me.BooleanField(required=True, default=True)

    severity = me.StringField(
        max_length=7,
        required=True,
        choices=(
            'LOW',
            'DEFAULT',
            'HIGH'),
        default='DEFAULT')

    feedback = me.StringField(
        max_length=8,
        required=True,
        choices=(
            'NEGATIVE',
            'NEUTRAL',
            'POSITIVE'),
        default='NEUTRAL')

    def __init__(self, *args, **kwargs):
        super(Notification, self).__init__(*args, **kwargs)
        if not self.created_date:
            self.created_date = datetime.now()

    def update_from(self, notification):
        self.created_date = notification.created_date
        self.expiry_date = notification.expiry_date
        self.user = notification.user
        self.organization = notification.organization
        self.summary = notification.summary
        self.body = notification.body
        self.html_body = notification.html_body
        self.resource = notification.resource
        self.unique = notification.unique
        self.action_link = notification.action_link
        self.severity = notification.severity
        self.feedback = notification.feedback


class EmailReport(Notification):
    '''
    Represents a notification corresponding to
    an email report
    '''
    subject = me.StringField(max_length=256, required=False, default="")
    email = me.EmailField(required=False)
    unsub_link = me.URLField(required=False)

    def update_from(self, notification):
        super(EmailReport, self).update_from(notification)

        self.subject = notification.subject
        self.email = notification.email
        self.unsub_link = notification.unsub_link


class InAppNotification(Notification):
    '''
    Represents an in-app notification
    '''
    model_id = me.StringField(required=True, default="")  # "autoscale_v1"
    model_output = me.DictField(
        required=True,
        default={})  # {"direction": "up"}

    dismissed = me.BooleanField(required=True, default=False)

    def update_from(self, notification):
        super(InAppNotification, self).update_from(notification)

        self.model_id = notification.model_id
        self.model_output = notification.model_output
        self.dismissed = notification.dismissed


class InAppRecommendation(InAppNotification):
    '''
    Represents an in-app recommendation
    '''
    pass
