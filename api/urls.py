from django.urls import path
from .requestHandlers import auth, chat, docs

urlpatterns = [

    # chat routes
    path('friends/', chat.friends, name='index'),
    path('conversation/<int:user_id>/', chat.conversation, name='conversation'),
    path('user/', chat.my_user, name='login'),
    path('profilePic/', docs.self_user_pic, name='login'),
    path('friends/<int:friend_id>/profilePic/',
         docs.friend_profile_picture, name='login'),

    # auth routes
    path('csrf/', auth.csrf, name='csrf'),
    path('login/', auth.do_login, name='login'),
    path('signup/', auth.signup, name='signup'),
    path('logout/', auth.do_logout, name='logout'),

]
