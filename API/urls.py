from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import *

router = routers.DefaultRouter()
router.register(r'', user, basename='users')

routerchat = routers.DefaultRouter()
routerchat.register(r'', ChatAPIView, basename='chatapi')

routermessage = routers.DefaultRouter()
routermessage.register(r'messages', MessageApiView, basename='messageapi')


router_test = routers.DefaultRouter()
router_test.register(r'', MessageViewSet, basename='sms')

urlpatterns = [
    path('', ChatsView.as_view(), name='chats'),
    path('user/', include(router.urls)),
    path('chats/', include(routerchat.urls)),
    path('chat/<int:chat_id>/', include(routermessage.urls)),
    path('chat/<int:chat_id>/peer/',
         ChatUserControlView.as_view({'get': "list",
                                      'patch': 'partial_update',
                                      "delete": "remove_members"}), name='peer'),


    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', RegisterView.as_view(), name='register'),


    #TEST
    path('sms/', include(router_test.urls)),
    path('celery/', CeleryTest.as_view(), name='celery'),
]