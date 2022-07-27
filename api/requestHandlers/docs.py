from django.http import FileResponse, JsonResponse
from http.client import NOT_FOUND
from urllib.request import Request
from django.http import JsonResponse
from api.models import ChatUser, FriendRelation
from django.db.models import Q
from django.contrib.auth.decorators import login_required


# user profile picture requet handler
@login_required()
def self_user_pic(request: Request):
    chatUser: ChatUser = request.user.chatuser
    if chatUser.profilePicturePath != None:
        return FileResponse(chatUser.profilePicturePath)
    return JsonResponse({
        'reason': 'user doesnt have a profile picture'
    }, status=400)


# friend profile picture request handler
@login_required()
def friend_profile_picture(request: Request, friend_id: int):
    cUser: ChatUser = request.user.chatuser

    if friend_id == cUser.id:
        return FileResponse(cUser.profilePicturePath)

    # find a relation that is complete and combines the current user and the friend
    relation = FriendRelation.objects.filter(
        Q(isComplete=True) & (Q(toUser=cUser.id, fromUser=friend_id) | Q(fromUser=cUser.id, toUser=friend_id))).first()

    if relation != None:
        friend = relation.fromUser if relation.fromUser.id == friend_id else relation.toUser

        # if the friend has a picture ...
        if friend.profilePicturePath != None:
            return FileResponse(friend.profilePicturePath)

        # if the friend doesn't have a picture
        else:
            return JsonResponse({
                'code': 'NO_PROFILE_PIC',
                'reason': 'Friend doesn\'t have a profile Picture'
            }, status=400)

    # if no relation is found ...
    else:
        return JsonResponse({
            'code': 'NOT_A_FRIEND',
            'reason': 'This user is not your friend'
        }, status=401)
