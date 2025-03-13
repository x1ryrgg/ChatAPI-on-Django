from django.urls import path, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'', FriendsViewSet, basename='friends')

urlpatterns = [
    path('requests/', FriendRequestView.as_view({'get': "list",
                                                 "post": "create",
                                                 'delete': 'destroy'}), name='requests'),
    path('requests/check/',FriendRequestView.as_view({'get': 'check_users'}),name='check'),

    path('responses/', FriendResponseView.as_view({'get': 'list'})),
    path('responses/<int:request_id>/', FriendResponseView.as_view({'post': 'create'})),

    path('friends/', include(router.urls)),
]
