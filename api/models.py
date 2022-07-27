from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Q


class ChatUser(models.Model):
    '''Chat user model'''

    # whether this user is connected or not
    isConnected = models.BooleanField()

    # path of the profile picture of the user
    profilePicturePath = models.FileField(
        upload_to='images/user_images', default=None, blank=True, null=True)

    friends = models.ManyToManyField(
        'self', symmetrical=True, through='FriendRelation')

    auth_user = models.OneToOneField(User, on_delete=models.CASCADE)

    def getConversation(self, otherUserId: int):
        return ChatMessage.objects.filter(
            Q(fromUser=self.id, toUser=otherUserId)
            | Q(toUser=self.id, fromUser=otherUserId))

    def getReceivedMessages(self, otherUserId: int):
        return ChatMessage.objects.filter(toUser=self.id, fromUser=otherUserId)


class FriendRelation(models.Model):

    # this is the user that sent the invitation
    fromUser = models.ForeignKey(
        to=ChatUser, on_delete=models.CASCADE, related_name='fromUser')

    # this is the user who received the invitation
    toUser = models.ForeignKey(
        to=ChatUser, on_delete=models.CASCADE, related_name='toUser')

    # this field represents the status of the friendship (accepted or not)
    isComplete = models.BooleanField(default=False)

    @staticmethod
    def getFriends(user: ChatUser):
        friendRelations = FriendRelation.objects.filter(
            Q(isComplete=True) & (Q(fromUser=user.id) | Q(toUser=user.id)))

        # get other side of every relation
        return [x.toUser if (x.fromUser.id == user.id) else (
            x.fromUser) for x in friendRelations]


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        ChatUser.objects.create(auth_user=instance, isConnected=True)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.chatuser.save()


class MessageStatus(models.IntegerChoices):
    '''Chat attachment type'''

    SENT = 1, 'sent'
    DELIVERED = 2, 'delivered'
    VIEWED = 3, 'viewed'

    @staticmethod
    def nameFromId(id):
        for x in MessageStatus.choices:
            if x[0] == id:
                return x[1]


class ParsableFromDict:
    def set(self, dict):
        self.__dict__.update(dict)


class ChatMessage(models.Model, ParsableFromDict):
    '''Chat message model'''

    # message content
    content = models.TextField(
        max_length=1024, default=None, blank=True, null=True)

    # the time this message was sent
    sendTime = models.DateTimeField(auto_now=True)

    # the time this message was seen
    seenTime = models.DateTimeField(default=None, blank=True, null=True)

    # message source user
    fromUser = models.ForeignKey(
        ChatUser, on_delete=models.CASCADE, related_name='from_user')

    # message destination user
    toUser = models.ForeignKey(
        ChatUser, on_delete=models.CASCADE, related_name='to_user')

    # message status
    status = models.IntegerField(
        choices=MessageStatus.choices,
        default=MessageStatus.SENT
    )


class AttachmentType(models.IntegerChoices):
    '''Chat attachment type'''

    # audio file attachment type (mp4, mkv ...)
    AUDIO = 1, 'audio'

    # video attachment type (mp4, webm ...)
    VIDEO = 2, 'video'

    # image attachment type (jpg, png ...)
    IMAGE = 3, 'image'

    # docuement attachment type (pdf, docx, ...)
    DOC = 4, 'document'

    # other types of attachments (zip, rar, psd ...)
    OTHER = 5, 'other'

    @staticmethod
    def nameFromId(id):
        for x in AttachmentType.choices:
            if x[0] == id:
                return x[1]


class ChatAttachment(models.Model):
    '''Chat attachment model'''

    # attachment type
    attachmentType = models.IntegerField(
        choices=AttachmentType.choices,
        default=AttachmentType.OTHER
    )

    # the attachment file
    attachment = models.FileField(upload_to='attachements/')

    # the message this attachment is related to
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)
