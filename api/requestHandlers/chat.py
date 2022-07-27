
from datetime import datetime
from http.client import NOT_FOUND
from urllib.request import Request
from django.http import FileResponse, JsonResponse
from api.models import ChatMessage, ChatUser, FriendRelation
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from api.serializers import ChatMessageSerializer, FriendSerializer, UserSerializer


@login_required()
def friends(request: Request):
    '''friend list request handler'''
    try:
        # get current chatuser
        chatUser = request.user.chatuser

        # get friend relations that include current user in either sides
        friends = [x.auth_user for x in FriendRelation.getFriends(chatUser)]

        # create a serializer
        serializer = FriendSerializer(friends, many=True, context={
            'user': chatUser
        })

        # return serialized data
        return JsonResponse({
            'friends': serializer.data
        }, safe=False)

    except ChatUser.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'reason': 'User not found'
        }, status=404)


def conversation(request: Request, user_id: int):
    '''messages conversation request handler'''

    chatUser = request.user.chatuser
    currentChatuserId = chatUser.id
    try:
        # get all messages that the current user is a part of
        messages = ChatMessage.objects.filter(
            Q(fromUser=currentChatuserId, toUser=user_id) | Q(fromUser=user_id, toUser=currentChatuserId))

        # set seen to current time on unseen messages
        for m in messages:
            if m.seenTime == None:
                m.seenTime = datetime.now()
                m.save()

        # create a seralizer
        serializer = ChatMessageSerializer(messages, context={
            'user': chatUser
        }, many=True)

        # return serialized data
        return JsonResponse({
            'messages': serializer.data
        }, safe=False)
    except ChatUser.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'reason': 'User not found'
        }, status=NOT_FOUND)


def my_user(request: Request):
    '''user details request handler'''
    # get current
    user = request.user

    if user.is_authenticated:
        return JsonResponse(UserSerializer(user).data)
    else:
        return JsonResponse({
            'status': 'Not logged in'
        }, status=401)
