from datetime import datetime
from time import mktime
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import serializers

from api.models import AttachmentType, ChatAttachment, ChatMessage, ChatUser, MessageStatus


class TimestampField(serializers.Field):
    def to_representation(self, value):
        return int(mktime(value.timetuple()))


class AttachmentSerializer(serializers.ModelSerializer):

    def to_representation(self, instance: ChatAttachment):
        obj = super().to_representation(instance)
        obj['attachmentType'] = AttachmentType.nameFromId(
            obj['attachmentType'])
        return obj

    class Meta:
        model = ChatAttachment
        fields = 'attachmentType,attachment'.split(',')


class ChatMessageDeserializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = 'content,fromUser,toUser'.split(',')


class ChatMessageSerializer(serializers.ModelSerializer):
    sendTime = TimestampField(required=False, allow_null=True)
    seenTime = TimestampField(required=False, allow_null=True)
    fromMe = serializers.SerializerMethodField()
    senderActive = serializers.SerializerMethodField()
    senderId = serializers.SerializerMethodField()
    chatattachment_set = AttachmentSerializer(many=True)

    def get_fromMe(self, message):
        mUser: ChatUser = self.context.get('user')
        return message.fromUser == mUser

    def get_senderId(self, message):
        return message.fromUser.id

    def get_senderActive(self, message):
        return message.fromUser.isConnected

    def to_representation(self, obj):
        obj = super().to_representation(obj)
        replaceAttr(obj, 'chatattachment_set', 'attachments')
        obj['status'] = MessageStatus.nameFromId(
            obj['status'])
        return obj

    class Meta:
        model = ChatMessage
        fields = 'content,sendTime,seenTime,fromMe,chatattachment_set,status,senderId,senderActive'.split(
            ',')


class ChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatUser
        fields = 'id,isConnected'.split(',')


def replaceAttr(obj, oldAttr, newAttr):
    obj[newAttr] = obj[oldAttr]
    del obj[oldAttr]


class UserSerializer(serializers.ModelSerializer):
    chatuser = ChatUserSerializer()

    class Meta:
        model = User
        fields = 'chatuser,username,first_name,last_name,email'.split(
            ',')

    def to_representation(self, obj):
        obj = super().to_representation(obj)
        if 'chatuser' in obj:
            for key in obj['chatuser']:
                obj[key] = obj['chatuser'][key]
            del obj['chatuser']

        replaceAttr(obj, 'first_name', 'firstName')
        replaceAttr(obj, 'last_name', 'lastName')

        return obj


class FriendSerializer(UserSerializer):
    unreadMessages = serializers.SerializerMethodField()

    def get_unreadMessages(self, user):

        # get current user fron context
        mUser: ChatUser = self.context.get('user')
        messages = ChatMessage.objects.filter(
            toUser=mUser.id, fromUser=user.chatuser.id, seenTime=None).all()
        mser = ChatMessageSerializer(messages, many=True)
        return mser.data

    class Meta:
        model = User
        fields = 'id,chatuser,username,first_name,last_name,email,unreadMessages'.split(
            ',')
