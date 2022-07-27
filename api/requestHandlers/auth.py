from urllib.request import Request
from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from api.serializers import FriendSerializer, UserSerializer


@require_http_methods(['POST'])
def do_login(request: Request):
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)
    ser = UserSerializer(user)

    if user is not None:
        login(request, user)
        return JsonResponse({
            'status': 'User logged in successfully',
            'user': ser.data
        })
    else:
        return JsonResponse({
            'status': 'User not logged in'
        }, status=401)


@require_http_methods(['POST'])
def signup(request: Request):
    try:
        username = request.POST['username']
        password = request.POST['password']
        User.objects.create_user(username, '', password)
        return JsonResponse({
            'status': 'User created successfully'
        })
    except:
        return JsonResponse({
            'status': 'Some error happened'
        }, status=400)


@login_required()
def do_logout(request):
    try:
        logout(request)
        return JsonResponse({
            'status': 'Logged out successfully'
        })
    except:
        return JsonResponse({
            'status': 'Could not log out'
        })


def csrf(request):
    return JsonResponse({'token': get_token(request)})
