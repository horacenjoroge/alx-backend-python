from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, UserViewSet

# Create a simple router without nested routers to avoid recursion
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    # Add specific endpoints for conversation messages if needed
    path('conversations/<uuid:conversation_pk>/messages/', 
         MessageViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='conversation-messages'),
]