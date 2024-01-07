from django.shortcuts import render, redirect
from django.shortcuts import render

from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm

from django.core import mail
from django.core.mail import EmailMessage
from django.conf import settings

from .models import User, ProfilePhotos, ActiveUser
from post.models import Post, Comment
from chat.models import Room

from .forms import SignUpForm, SignInForm, UpdateUserForm
from post.forms import PostForm


def error_404(request, exception):
    """
    Error view for incorrect urls.
    """
    return render(request, "errors/404.html")


def sign_up(request):
    """
    Signing up user.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            ActiveUser.objects.create(
                user=user,
                is_online=True
            )
            return redirect('users:home')
    else:
        form = SignUpForm()

    context = {
        'form': form
    }
    return render(request, 'users/signup.html', context)


def sign_in(request):
    """
    Signing in user.
    """
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                user_status = ActiveUser.objects.get(
                    user_id=user.id
                )
                user_status.is_online = True
                user_status.save()
                return redirect('users:home')
    else:
        form = SignInForm()

    context = {
        'form': form
    }
    return render(request, 'users/signin.html', context)


@login_required
def sign_out(request):
    """
    Signing out user.
    """
    user_status = ActiveUser.objects.get(
        user_id=request.user.id
    )
    logout(request)
    user_status.is_online = False
    user_status.save()
    return redirect('users:sign-in')


@login_required
def home(request):
    """
    Landing page after successful authentication,
    """
    user = request.user
    context = {
        "user": user
    }
    return render(request, "users/home.html", context)


@login_required
def photos(request, user_id): 
    """
    User profile photos.
    """
    user = User.objects.get(pk=user_id)
    profile_photos = ProfilePhotos.objects.filter(user=user_id)

    items_per_page = 9
    paginator = Paginator(profile_photos, items_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        "user": user,
        "page": page
    }
    return render(request, "users/photos.html", context)


@login_required
def apply_photo(request, photo_id): 
    """
    Setting a photo as a profile photo.
    """
    user = User.objects.get(pk=request.user.id)
    profile_photo = ProfilePhotos.objects.get(pk=photo_id)
    if user.profile_photo != profile_photo.photo:
        user.profile_photo = profile_photo.photo
        user.save()
        # delete to get rid of duplicates
        profile_photo.delete()
    return redirect('users:photos', user_id=user.id)


@login_required
def edit_account(request): 
    """
    Editing current user's account.
    """
    current_user = request.user
    initial_data = {'date_of_birth': current_user.date_of_birth.strftime('%d-%m-%Y')}
    form = UpdateUserForm(instance=request.user, initial=initial_data)
    if request.method == 'POST':
        form = UpdateUserForm(data=request.POST, files=request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:edit-account')
        
    context = {
        'current_user': current_user,
        'form': form,
    }
    return render(request, 'users/edit_account.html', context)


class PasswordsChangeView(PasswordChangeView):
    """
    Changing current user's password.
    """
    login_required = True
    form_class = PasswordChangeForm
    success_url = reverse_lazy('users:edit-account')


@login_required
def delete_photo(request, photo_id):
    """
    Deleting current user's photo.
    """
    user = request.user
    try:
        photo = ProfilePhotos.objects.get(
            Q(user=user.id) & Q(pk=photo_id)
        )
        # if user delete their current one
        if user.profile_photo == photo.photo:
            user.profile_photo = None
            user.save()

        photo.delete()
        return redirect('users:photos', user_id=user.id)
    except ProfilePhotos.DoesNotExist:
        return redirect('users:photos', user_id=user.id)
    

@login_required
def search_user(request):
    """
    Searching for users.
    """
    if request.method == 'GET':
        current_user = request.user
        query = request.GET.get('q')
        # considering long searches with spaces in between
        long_query = [item for item in request.GET.get('q').split(" ") if item != ""]
        if query:
            if len(long_query) > 1:
                potential_fn, potential_ln = long_query[0], long_query[1]
                users = User.objects.filter(
                    Q(first_name__icontains=potential_fn) | Q(last_name__icontains=potential_ln)
                ).exclude(pk=current_user.pk)
            else:
                users = User.objects.filter(
                    Q(first_name__icontains=query) | Q(last_name__icontains=query)
                ).exclude(pk=current_user.pk)
        if users:
            paginator = Paginator(users, 3) 
            page_number = request.GET.get('page')

            # the first page_number is evaluated as none.
            if page_number == None:
                page_number = 1

            page = paginator.get_page(page_number)
            no_results = False

        else:
            paginator = Paginator([], 3)
            page_number = request.GET.get('page')
            page = paginator.get_page(page_number)
            no_results = True

        context = {
            'searched': query,
            'page': page,
            'no_results': no_results
        }
        return render(request, 'users/search.html', context)
    else:
        print("Error: an error occured during the request.")


@login_required
def delete_user(request):
    """
    Deleting current user.
    """
    current_user = request.user
    # deleting user from groups if they are members of any
    try:
        rooms =  Room.objects.rooms = Room.objects.filter(
            members__contains=[current_user.pk]
        )
        # user is an owner
        for room in rooms:
            if room.user.pk == current_user.pk:
                room.delete()
            # user is a regular member
            else:
                member_id = str(current_user.pk)
                room.members.remove(member_id)
                room.save()
    except Room.DoesNotExist:
        pass
    current_user.delete()
    return redirect('index')
    

@login_required
def user_posts(request, user_id):
    """
    Viewing a user's posts.
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user  
            post.save()
            return redirect('post:feed')  
    else:
        form = PostForm()

    user = User.objects.get(pk=user_id)
    posts = Post.objects.filter(user_id=user.id).order_by('-date_created')
    comments = Comment.objects.filter(post__in=posts).select_related('user', 'post')
    items_per_page = 10
    paginator = Paginator(posts, items_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        "user": user,
        "form": form,
        "page": page,
        "comments": comments
    }
    return render(request, "users/user_posts.html", context)


def password_reset(request): #uid
    connection = mail.get_connection()
    connection.open()

    email = EmailMessage(
        'Reset your password by clicking on the following link:',
        'THIS IS THE BODY YOHOOOO 127.0.0.1:8000', 
        settings.EMAIL_HOST_USER,
        ['meraghnir93@gmail.com'],
        connection=connection,
    )

    connection.send_messages([email])
    connection.close()

    return render(request, 'users/password_reset.html')
