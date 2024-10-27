from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import ChatMessageForm

# Create your views here.
@login_required
def chat_view(request):
    chat_group=get_object_or_404(ChatGroup, group_name='global-chat')
    chat_messages=chat_group.chat_messages.all()[:30]
    form= ChatMessageForm()


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


    context={
        'chat_messages': chat_messages,
        'form':form,
    }

    return render(request,'chat/chat.html', context)

