import random
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404
from .forms import TweetForm
from .models import Tweet
from .serializers import TweetSerializer, TweetActionSerializer
from django.utils.http import is_safe_url
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes 
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

ALLOWED_HOSTS = settings.ALLOWED_HOSTS

# Create your views here.
def home(request, *args, **kwargs):
    print(request.user or None)
    return render(request, 'pages/home.html', context={}, status=200)

@api_view(['POST'])
# @authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_tweet(request, *args, **kwargs):
    serializer = TweetSerializer(data=request.POST)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response({}, status=400)

@api_view(['GET'])
def tweet_list(request, *args, **kwargs):
    qs = Tweet.objects.all()
    serializer = TweetSerializer(qs, many=True)
    tweet_lists = [x.serialize() for x in qs]
    data = {
        "isUser": False, 
        "response": tweet_lists
    }
    return Response(serializer.data)

@api_view(['GET'])
def tweet_detail(request, tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({}, status=404)
    obj = qs.first()
    serializer = TweetSerializer(obj)
    return Response(serializer.data, status=200)

@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def tweet_delete(request, tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({}, status=404)
    qs = qs.filter(user=request.user)
    if not qs.exists():
        return Response({"message": "You cannot delete this tweet"}, status=200)
    obj = qs.first()
    obj.delete()
    return Response({"message": "Tweet Removed"}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tweet_action(request, tweet_id, *args, **kwargs):
    print(request.POST, request.data)
    '''
    Id is required. Actions are Like, Unlike, Retweet
    '''
    serializer = TweetActionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data = serializer.validated_data
        tweet_id = data.get('id')
        action = data.get('action')
        content = data.get("content")
        qs = Tweet.objects.filter(id=tweet_id)
        if not qs.exists():
            return Response({}, status=404)
        qs = qs.filter(user=request.user)
        obj = qs.first()
        if action == "like":
            obj.likes.add(request.user)
            serializer = TweetSerializer(obj)
            return Response(serializer.data, status=200)
        elif action == "unlike":
            obj.likes.remove(request.user)
        elif action == "retweet":
            # This is To-Do
            new_tweet = Tweet.objects.create(
                user=request.user,
                parent=obj,
                content=content)
            serializer = TweetSerializer(new_tweet)
            return Response(serializer.data, status=200)
    return Response({"message": "Tweet Liked!"}, status=200)


'''def create_tweet_django(request, *args, **kwargs):
    
    # REST API
    
    user = request.user
    if not request.user.is_authenticated:
        user = None
        if request.is_ajax():
            return JsonResponse({}, status=401)
        return redirect(settings.LOGIN_URL)
    form = TweetForm(request.POST or None)
    next_url = request.POST.get("next") or None
    print('next_url', next_url)
    if form.is_valid():
        obj = form.save(commit=False)
        # Do other Form Related Logic
        obj.user = request.user
        obj.save()
        if request.is_ajax():
            return JsonResponse(obj.serialize(), status=201)
        if next_url != None and is_safe_url(next_url, ALLOWED_HOSTS):
            return redirect(next_url)
        form = TweetForm()
    if form.errors:
        if request.is_ajax:
            return JsonResponse(form.errors, status=400)
    return render(request, 'components/form.html', context={'form':form})


def tweet_list_django(request, *args, **kwargs):
    qs = Tweet.objects.all()
    tweet_lists = [x.serialize() for x in qs]
    data = {
        "isUser": False, 
        "response": tweet_lists
    }
    return JsonResponse(data)

def tweet_detail_django(request, tweet_id, *args, **kwargs):
    """
    REST API VIEW
    Consume by JavaScript,Java,Swift
    return JSON data
    """
    data = {
        "id": tweet_id,
    }
    status = 200

    try:
        obj = Tweet.objects.get(id=tweet_id)
        data['content'] = obj.content
    except:
        data['messsage'] = "Content Not Found"
        status = 404

    return JsonResponse(data, status=status) # json.dumps
'''