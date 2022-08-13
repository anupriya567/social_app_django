from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from . models import Follow, LikePost, Profile, Post
from itertools import chain
import random
from datetime import datetime
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect
     

def FetchProfilesForPosts(feed_list):
    all_post_username = []
    all_post_user_obj = []
    all_post_profile = []

    for feed in feed_list:
        all_post_username.append(feed.user)

    for user in all_post_username:
        all_post_user_obj.append(User.objects.get(username = user))

    for obj in all_post_user_obj:
       all_post_profile.append(Profile.objects.get(user = obj))

    return all_post_profile   


def FetchUserSuggestions(request, user_following):
    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username = user)
        user_following_all.append(user_list)

    # suggestions_list  => users which I am not following currently
    # looping through the list of all users and putting all those user which are not in user_following_all list
    suggestions_list = [x for x in list(all_users) if x not in list(user_following_all)]
    
    current_user = User.objects.filter(username = request.user.username)
    final_suggestions_list = [x for x in list(suggestions_list) if x not in list(current_user)]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user = ids)
        username_profile_list.append(profile_lists)   

    suggestions_username_profile_list = list(chain(*username_profile_list))
    return suggestions_username_profile_list


@login_required(login_url = 'signin')
def index(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)
    
    user_following_list = [] 
    feed = []
    user_following = Follow.objects.filter(follower = request.user.username)

    for user in user_following:
        # having names of users whom I am following
        user_following_list.append(user.username)

    for user in user_following_list:
        posts = Post.objects.filter(user = user)
        feed.append(posts)
    
    self_post = Post.objects.filter(user = request.user.username)
    feed.append(self_post)

    feed_list = list(chain(*feed))
    # sort feed list acc. to created time
    feed_list.sort(key = lambda x: x.created_at, reverse=True)
    all_post_profile = FetchProfilesForPosts(feed_list)
    
    suggestions_username_profile_list = FetchUserSuggestions(request, user_following)
    

    return render(request, 'index.html',{'user_profile':user_profile, 'posts_profiles': zip(feed_list,all_post_profile), 'suggestions_username_profile_list': suggestions_username_profile_list[:4]  } )


@login_required(login_url = 'signin')
def search(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)
    
    if request.method == 'POST':
        username = request.POST['username']
        username_objs = User.objects.filter(username__icontains = username)

        username_profile_ids = []
        username_profile_list = []

        for user_obj in username_objs:
            username_profile_ids.append(user_obj.id)
        
        for id in username_profile_ids:
            profile = Profile.objects.filter(id_user = id)
            username_profile_list.append(profile)


        username_profile_list = list(chain(*username_profile_list))    
    
        return render(request, 'search.html',{'user_profile':user_profile, 'username_profile_list': username_profile_list, 'username': username} )
    return redirect('/')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2'] 
        
        if(password == password2):
            if User.objects.filter(email = email).first():
                messages.info(request, 'Email already exits')
                return redirect('signup')
            elif User.objects.filter(username = username).first():
                messages.info(request, 'Username already exits')
                return redirect('signup')    
            else:
                user = User.objects.create_user(username = username, email = email, password = password)    
                user.save()
                # result = send_email(username, email)
                # print(result)

                # log user in and redirect to settings page
                user_login = auth.authenticate(username = username, password = password )
                auth.login(request, user_login)
                

                user_model = User.objects.get(username = username)
                new_profile = Profile.objects.create(user = user_model, id_user = user_model.id)
                new_profile.save()

                return redirect('settings')

        else:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')
    else:     
       return render(request, 'signup.html')

def signin(request): 

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username = username, password = password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('signin')    
   
    return render(request, 'signin.html')    

@login_required(login_url = 'signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url = 'signin')
def upload(request):
    if request.method == 'POST':
        image = request.FILES.get('image_upload')
        caption = request.POST.get('caption')
        # print(request.user.username)
        upload_post = Post.objects.create( user =request.user.username, image = image, caption= caption)
        upload_post.save()
        return redirect('/')
    else:
        return redirect('/')    


def delete_post(request,post_id):
    post = Post.objects.get(pk=post_id)
    if(post.user == request.user.username):
        # print('yes')
        post.delete()
    else:
        messages.error(request,("Access Denied! You can't delete this "))   
    return redirect('index')

def like_post(request,post_id):
    post = Post.objects.get(id = post_id)
    like = LikePost.objects.filter(post_id = post_id, username = request.user.username)
    
    if not like:
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        likepost = LikePost.objects.create(post_id = post_id, username = request.user.username)
        likepost.save() 
        
    else:
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        like.delete()     
    return redirect('/')
 
@login_required(login_url = 'signin')
def profile(request,pk):
    user_object = User.objects.get(username = pk)
    user_profile = Profile.objects.get(user = user_object)
    user_posts = Post.objects.filter(user = pk)
    user_post_length = len(user_posts)

    if(Follow.objects.filter(follower = request.user.username, username = pk).first()):
        button_text = 'UNFOLLOW'

    else:
        button_text = 'FOLLOW'
        user_posts = Post.objects.none()

    user_followers = len(Follow.objects.filter(username = pk))
    user_following = len(Follow.objects.filter(follower = pk))

    context = {
        'user_profile': user_profile, 
        'user_posts': user_posts,
        'user_post_length' : user_post_length,
        'button_text' : button_text,
        'user_followers': user_followers,
        'user_following': user_following
    }
    
    return render(request, 'profile.html',context)


def follow(request):
    if request.method == 'POST':
        username = request.POST['username']
        follower = request.POST['follower']
        obj =  Follow.objects.filter(username = username, follower = follower)
        if not obj:
            # print('addd')
            follow_user = Follow.objects.create(username = username, follower = follower)
            follow_user.save()
            return redirect('profile/'+ username)
        else:
            # print('delete')
            obj.delete()  

    return redirect('/')


def unfollow(request, pk):
    obj =  Follow.objects.filter(username = pk, follower = request.user.username)
    obj.delete() 
    return redirect('/') 

@login_required(login_url = 'signin')
def settings(request):
    user_profile = Profile.objects.get(user = request.user)
    # print(request.user) 
    if request.method == 'POST':
        if request.FILES.get('image') != None:
            user_profile.profileimage = request.FILES.get('image')    

        user_profile.bio = request.POST['bio']
        user_profile.location = request.POST['location']
        user_profile.save()
        return redirect('index')

    
    return render(request, 'setting.html', {'user_profile': user_profile})

# def send_email(username, email):
#     subject = "Registered Successfully"
#     message = f"Hi {username}, you are now successfully registered"
#     from_email = ''
#     result = send_mail(subject, message, from_email, [email])
#     print("sent")  
#     return result     