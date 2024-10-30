from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import ChatMessageForm
from django.http import Http404


# Create your views here.
@login_required
def chat_view(request, chatroom_name='global-chat'):
    chat_group=get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages=chat_group.chat_messages.all()[:30]
    form= ChatMessageForm()

    other_user = None
    if chat_group.isPrivate:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break

    if request.htmx:
        form=ChatMessageForm(request.POST)
        if form.is_valid:
            message=form.save(commit=False)
            message.author= request.user
            message.group= chat_group
            form_context={
                'message':message,
                'user':request.user
            }
            message.save()
        return render(request, 'chat/partials/chat_messages_p.html', form_context)


    context = {
        'chat_messages' : chat_messages, 
        'form' : form,
        'other_user' : other_user,
        'chatroom_name' : chatroom_name,
        # 'chat_group' : chat_group
    }

    return render(request,'chat/chat.html', context)

@login_required
def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect('home')
    
    other_user = User.objects.get(username = username)
    my_chatrooms = request.user.chat_groups.filter(isPrivate=True)
    
    
    if my_chatrooms.exists():
        for chatroom in my_chatrooms:
            if other_user in chatroom.members.all():
                return redirect('chatroom', chatroom.group_name)
    else:
        chatroom = ChatGroup.objects.create(isPrivate = True)
        chatroom.members.add(other_user, request.user)

    return redirect('chatroom', chatroom.group_name)

