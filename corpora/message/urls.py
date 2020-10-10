from django.urls import path

from message.views import MessageView

urlpatterns = [
    path('<pk>/', MessageView.as_view(), name='messageDetail'),
]
