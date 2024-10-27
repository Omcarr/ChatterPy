from channels.generic.websocket import WebsocketConsumer, async_to_sync
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from .models import ChatGroup, GroupMessage
import json
from asgiref.sync import async_to_sync

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name'] 
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)
        
        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )
        
        # # add and update online users
        # if self.user not in self.chatroom.users_online.all():
        #     self.chatroom.users_online.add(self.user)
        #     self.update_online_count()
        
        self.accept()
        
        
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )
        # # remove and update online users
        # if self.user in self.chatroom.users_online.all():
        #     self.chatroom.users_online.remove(self.user)
        #     self.update_online_count() 
        
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']
        
        message = GroupMessage.objects.create(
            body = body,
            author = self.user, 
            group = self.chatroom 
        )
        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )
        
           
    def message_handler(self, event):
        message_id = event['message_id']
        message = GroupMessage.objects.get(id=message_id)
        context = {
            'message': message,
            'user': self.user,
            'chat_group': self.chatroom
        }
        html = render_to_string("chat/partials/chat_message_p.html", context=context)
        
        # Send this HTML as a message for HTMX to swap
        self.send(text_data=json.dumps({
            'html': html
        }))