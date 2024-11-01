from django.db import models
from django.contrib.auth.models import User
from shortuuid import uuid
# Create your models here.
class ChatGroup(models.Model):
    #Dms
    group_name=models.CharField(max_length=50, unique=True, default=uuid)

    #private gc
    groupchat_name = models.CharField(max_length=50, null=True, blank=True)
    admin = models.ForeignKey(User, related_name='groupchats', blank=True, null=True, on_delete=models.SET_NULL)

    #general chat properties
    users_online=models.ManyToManyField(User, related_name="online_in_groups", blank=True)
    members=models.ManyToManyField(User, related_name="chat_groups", blank=True)
    isPrivate=models.BooleanField(default=False)


    # Background image for the chat room
    #background_img = models.ImageField(upload_to='chat_backgrounds/', null=True, blank=True)

    def __str__(self) -> str:
        return self.group_name

    def save(self, *args, **kwargs):
        if not self.group_name:
            self.group_name = uuid()
        super().save(*args, **kwargs)
    
        

class GroupMessage(models.Model):
    group=models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE)
    author=models.ForeignKey(User, on_delete=models.CASCADE)
    body=models.CharField(max_length=300)
    created=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username}: {self.body}'
    
    class Meta:
        ordering=['-created']

