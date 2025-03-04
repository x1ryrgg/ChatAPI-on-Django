from django.urls import path, include
from rest_framework import routers

from .views import *



urlpatterns = [
    path('requests/', FriendRequestView.as_view({'get': "list",
                                                 "post": "create",
                                                 'delete': 'destroy'}), name='requests'),
    path('responses/', FriendResponseView.as_view({'get': 'list'})),
    path('responses/<int:request_id>/', FriendResponseView.as_view({'post': 'create'})),
]
