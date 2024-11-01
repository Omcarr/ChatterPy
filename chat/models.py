from django.db import models
from django.contrib.auth.models import User
from shortuuid import uuid
import os
from PIL import Image

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
    body=models.CharField(max_length=300,null=True)
    file=models.FileField(upload_to='files/', blank=True, null=True)
    created=models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None


    def __str__(self):
            if self.body:
                return f'{self.author.username} : {self.body}'
            elif self.file:
                return f'{self.author.username} : {self.filename}'
    
    class Meta:
        ordering = ['-created']
    

    #pillow verifies if its a image, to avoid trying to display pdf or zip as an img
    @property    
    def is_image(self):
        try:
            image = Image.open(self.file) 
            image.verify()
            return True 
        except:
            return False
