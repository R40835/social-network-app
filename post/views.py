from django.db.models import Q
from django.urls import reverse
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect

from .models import Post, Comment, Like
from notification.models import PostNotification
from .forms import PostForm, CommentForm , UpdatePostForm, UpdateCommentForm


@login_required
def feed(request):
    """
    Public feed for all users' interactions.
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user  
            post.save()
            return HttpResponseRedirect(reverse('post:feed'))  
    else:
        form = PostForm()
        
    posts = Post.objects.all().order_by('-date_created')
    comments = Comment.objects.filter(post__in=posts).select_related('user', 'post')
    items_per_page = 10
    paginator = Paginator(posts, items_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'form': form,
        'page': page,
        'comments': comments
    }
    return render(request, "post/feed.html", context)


@login_required
def create_post(request):
    """
    Creating a post.
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user  
            post.save()
            return HttpResponseRedirect(reverse('post:feed'))  
    else:
        form = PostForm()

    context = {
        'form': form
    }
    return render(request, 'post/create_post.html', context)


@login_required
def create_comment(request, post_id):
    """
    Creating a comment.
    """
    user = request.user
    post = Post.objects.get(pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()

            if post.user.id != user.id:
                PostNotification.objects.create(
                    post=post,
                    sender=user,
                    recipient=post.user,
                    notification_type='Comment'
                ) 

            return HttpResponseRedirect(reverse('post:post', args=[post_id]))
    else:
        form = CommentForm()

    context = {
        'user': user,
        'form': form, 
        'post': post
    }
    return render(request, 'post/create_comment.html', context)


@login_required
def like_post(request, post_id):
    """
    Liking a post.
    """
    user = request.user
    post = get_object_or_404(Post, pk=post_id)
    if user.is_authenticated:
        try:
            user.like_post(post)
            if post.user != request.user:
                PostNotification.objects.create(
                    post=post,
                    sender=request.user,
                    recipient=post.user,
                    notification_type='Like'
                ) 
            return JsonResponse({'post_id': post.id, 'likes': post.likes, 'liked': True})
        except Like.DoesNotExist:
            print("Error while liking the post")
    return JsonResponse({'error': 'User not authenticated'})


@login_required
def unlike_post(request, post_id):
    """
    Unliking a post.
    """
    user = request.user
    post = get_object_or_404(Post, pk=post_id)
    if user.is_authenticated:
        try:
            # deletes the like from the db and substracts 1 from post likes
            user.unlike_post(post)
            return JsonResponse({'post_id': post.id, 'likes': post.likes, 'liked': False})
        except Like.DoesNotExist:
            print("Error while unliking the post")
    return JsonResponse({'error': 'User not authenticated'})


@login_required
def post(request, post_id):
    """
    Post dedicated view.
    """
    post = Post.objects.get(pk=post_id)
    if post.user_id == request.user.id:
        notifications = PostNotification.objects.filter(post_id=post_id)
        notifications.update(is_read=True)

    comments = Comment.objects.filter(post_id=post.id).order_by('-timestamp')
    items_per_page = 3
    paginator = Paginator(comments, items_per_page)
    page_number = request.GET.get('page')
    comments = paginator.get_page(page_number)

    context = {
        'post': post,
        'page': comments
    }
    return render(request, "post/post.html", context)


@login_required
def edit_post(request, post_id):
    """
    Editing a post.
    """
    user = request.user
    post = Post.objects.get(
        Q(user=user.id) & Q(pk=post_id)
    )
    if request.method == 'POST':
        form = UpdatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            clear_photo = form.cleaned_data.get('clear_photo')
            if clear_photo:
                if post.photo:
                    post.photo.delete(save=False)
                post.photo = None
            form.save()
            return HttpResponseRedirect(reverse('post:post', args=[post_id]))
    else:
        if post.photo:
            post_photo = post.photo
        else:
            post_photo = None
        form = UpdatePostForm(instance=post)

    context = {
        'form': form,
        'post_photo': post_photo
    }
    return render(request, 'post/edit_post.html', context)


@login_required
def edit_comment(request, comment_id):
    """
    Editing a comment.
    """
    user = request.user
    comment = Comment.objects.get(
        Q(user=user.id) & Q(pk=comment_id)
    )
    post = Post.objects.get(
        comment=comment
    )
    form = UpdateCommentForm(instance=comment)  
    if request.method == 'POST': 
        form = UpdateCommentForm(data=request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('post:post', args=[post.id]))
        
    context = {
        'post': post,
        'user': user,
        'form': form
    }
    return render(request, 'post/edit_comment.html', context)


@login_required
def delete_comment(request, comment_id):
    """
    Deleting a comment.
    """
    user = request.user
    comment = Comment.objects.get(
        Q(user=user.id) & Q(pk=comment_id)
    )
    post_id = comment.post.id
    comment.delete()
    return HttpResponseRedirect(reverse('post:post', args=[post_id]))


@login_required
def delete_post(request, post_id): 
    """
    Deleting a post.
    """
    user = request.user
    post = Post.objects.get(
        Q(user=user.id) & Q(pk=post_id)
    )
    post.delete() 
    return HttpResponseRedirect(reverse('post:feed'))


@login_required
def likers(request, post_id):
    """
    Post likers view; rendered in a modal.
    """
    post = get_object_or_404(Post, pk=post_id)
    # Getting all the Like instances related to the post
    users_liked = post.like_set.all()  
    likers = [like.user for like in users_liked]

    context = {
        'likers': likers
    }
    return render(request, "post/likers.html", context)
