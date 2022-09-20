# social_app
[View demo video here](https://youtu.be/vVP9VODJMWs)</br>
It is like a social book where you can-
- create your account
- upload your photos, delete your post
- follow your friends, unfollow them
- view their profile, view their uploads
- search for your friends
- it also shows suggested users, any 5 users, each time you reload will 
- show different random users from list

## 1). Display posts

Firstly, we are displaying all posts from the Post Model
```
@login_required(login_url = 'signin')
def index(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)
    
    posts = Post.objects.all()
    return render(request, 'index.html',{'user_profile':user_profile, 'posts': posts} )
```
then we added a functionality,</br>

we can see our post and the users whom we are following</br>
```
@login_required(login_url = 'signin')
def index(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)
    
    user_following_list = []
    feed = []
    user_following = Follow.objects.filter(follower = request.user.username)

    for user in user_following:
        user_following_list.append(user.username)


    for user in user_following_list:
        posts = Post.objects.filter(user = user)
        feed.append(posts)
        
    self_post = Post.objects.filter(user = request.user.username)
    feed.append(self_post)
    
    feed_list = list(chain(*feed))

    # posts = Post.objects.all()
    return render(request, 'index.html',{'user_profile':user_profile, 'posts': feed_list} )
```
* Now, there is an issue here, 
* now, how would be able to increase our network ie. how we would follow more users now
* earlier when all post were visible, by clicking username on post, we can go to his profile and can follow them from there

Solution :
> Add Search Functionality:</br>
  We can search users </br>
  can open their profile and follow them</br>
```
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

```

### User Suggestions to increase our network

* From all users, we find the users whom we are not following currently, they will be shown up as suggestions 
* Will be shown only 4 at a time and in random order each time

```
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
    return suggestions_username_profile_
```
       
> Problem - 
 each time even if we just load the screen, will send a get request to index, view for index will execute, each we have to load large no. of posts


## 2). itertools — Functions creating iterators for efficient looping
> chain() - chain.from_iterable(['ABC', 'DEF']) --> A B C D E F

```
 for user in user_following_list:
        posts = Post.objects.filter(user = user)
        feed.append(posts)
    
    self_post = Post.objects.filter(user = request.user.username)
    feed.append(self_post)

    feed_list = list(chain(*feed))
```
    
Let's understand this:
> user_following_list: [A, B, C, H] (4 users)

```
 for user in user_following_list:
        posts = Post.objects.filter(user = user)
        feed.append(posts)
```
> feed = [ [Ap, Ap, Ap, Ap, Ap], [Bp, Bp], [Cp, Cp, Cp], [Dp]]
```
self_post = Post.objects.filter(user = request.user.username)
    feed.append(self_post)
```
> feed = [ [Ap, Ap, Ap, Ap, Ap], [Bp, Bp], [Cp, Cp, Cp], [Dp], [Up,Up,Up]]
on applying chain iterator

> feed = [Ap, Ap, Ap, Ap, Ap, Bp, Bp, Cp, Cp, Cp, Dp, Up,Up,Up]


### 3).  Python | Iterate over multiple lists simultaneously

> zip() : In Python 3, zip returns an iterator. zip() function stops when anyone of the list of all the lists gets exhausted. In simple words, it runs till the                   smallest of all the lists.

```
import itertools 
  
num = [1, 2, 3]
color = ['red', 'while', 'black']
value = [255, 256]
  
# iterates over 3 lists and executes 
# 2 times as len(value)= 2 which is the
# minimum among all the three 
for (a, b, c) in zip(num, color, value):
     print (a, b, c)
```
> you need zip() but it isn't defined in jinja2 templates.</br>
 one solution is zipping it before render_template function is called, like:

#### eg1-
view function:
```
return render_template('form_result.html',type=type,reqIDs_msgs_rcs=zip(IDs,msgs,rcs))
template:

{% for reqID,msg,rc in reqIDs_msgs_rcs %}
<h1>ID - {{ID}}</h1>
{% if rc %}
<h1>Status - {{msg}}!</h1>
{% else %}
<h1> Failed </h1>
{% endif %}
{% endfor %}
```
#### eg2-
in views- 
```
return render(request, 'index.html',{'user_profile':user_profile, 'posts_profiles': zip(feed_list,all_post_profile),} )
```
template- 
```
 {%for post, profile in posts_profiles %}
<div class="bg-white shadow rounded-md  -mx-2 lg:mx-0">
    
  <!-- post header-->
    <div class="flex justify-between items-center px-4 py-3">
      <div class="flex flex-1 items-center space-x-4">
          <a href="/profile/{{post.user}}">
              <div class="bg-gradient-to-tr from-yellow-600 to-pink-600 p-0.5 rounded-full">  
                  <img src="{{profile.profileimage.url}}" class="bg-gray-200 border border-white rounded-full w-8 h-8">
              </div>
          </a> 
          <span class="block font-semibold "><a href="/profile/{{post.user}}">@{{post.user}}</a></span>
      </div>


    <div>

```
### 4). Downloading a post

```
<a href="/images/myw3schoolsimage.jpg" download>
```

### 5). Difference b/w get() and filter()

> filter returns a queryset object</br>
  get returns the required object.

#### filter()
* If you use filter(), you typically do this whenever you expect more than just one object that matches your criteria. 
* If no item was found matching your criteria, filter() returns am empty queryset without throwing an error.

#### get()
* If you use get(), you expect one (and only one) item that matches your criteria. 
* Get throws an error if the item does not exist or if multiple items exist that match your criteria.
* You should therefore always use if in a try.. except .. block or with a shortcut function like get_object_or_404 in order to handle the exceptions properly.


### 6). Opening the profile of another user 
 * if not following the user, posts are not visible
 
 ```
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
 ```
### 7). Sort all display posts acc. to created_time

 feed_list is list of objects
```
    feed_list = list(chain(*feed))
    # sort feed list acc. to created time
    feed_list.sort(key = lambda x: x.created_at, reverse=True)
```    

> error on changing 
    user = Fk
    all other fields to Fk

    ERRORS:
    core.Follow.follower: (fields.E304) Reverse accessor 'User.follow_set' for 'core.Follow.follower' clashes with reverse accessor for 'core.Follow.main_user'.
            HINT: Add or change a related_name argument to the definition for 'core.Follow.follower' or 'core.Follow.main_user'.
    core.Follow.main_user: (fields.E304) Reverse accessor 'User.follow_set' for 'core.Follow.main_user' clashes with reverse accessor for 'core.Follow.follower'.
        HINT: Add or change a related_name argument to the definition for 'core.Follow.main_user' or 'core.Follow.follower'.


