from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import *

router = routers.DefaultRouter()
router.register(r'', User, basename='users')

routerchat = routers.DefaultRouter()
routerchat.register(r'', ChatAPIView, basename='chatapi')

routermessage = routers.DefaultRouter()
routermessage.register(r'', MessageApiView, basename='messageapi')


router_test = routers.DefaultRouter()
router_test.register(r'', MessageViewSet, basename='sms')

urlpatterns = [
    path('user/', include(router.urls)),
    path('', include(routerchat.urls), name='chats'),
    path('chat/<int:id>/messages/', MessageApiView.as_view({'get': "list",
                                                            "post": 'create'}), name='messages'),
    path('chat/<int:id>/messages/<int:message_id>/', MessageApiView.as_view({'get': 'retrieve',
                                                                             'delete': 'destroy'}), name='message'),
    path('chat/<int:id>/peer/',
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