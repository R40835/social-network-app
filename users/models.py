from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from PIL import Image
from post.models import Like
from friend.models import Friendship, FriendRequest
from django.core.exceptions import ValidationError
from social_network import settings


# Using a custom user model, refer to the documentation:
# https://docs.djangoproject.com/en/4.2/topics/auth/customizing/ 


class MyUserManager(BaseUserManager):
    def create_user(self, email, date_of_birth, password=None, **kwargs):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, date_of_birth, password=None, **kwargs):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            date_of_birth=date_of_birth,
            **kwargs
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    first_name = models.CharField(
        max_length=20, 
        unique=False, 
        blank=False,
    )
    last_name = models.CharField(
        max_length=20, 
        unique=False, 
        blank=False
    )
    email = models.EmailField(
        verbose_name="Email Address",
        max_length=255,
        unique=True,
    )
    date_of_birth = models.DateField(
        blank=False, 
        unique=False
    )
    profile_photo = models.ImageField(
        upload_to="profile_photos/",
        blank=True,
        null=True,
    )
    liked_posts = models.ManyToManyField(
        'post.Post', 
        through='post.Like', 
        related_name='liked_users',
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "date_of_birth"]

    def __str__(self):
        """
        String representation of the object.
        """
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    
    def save(self, *args, **kwargs):
        """
        Override the save method to handle user profile photo resizing 
        and save them in DB.
        """
        # if the user is being created for the first time
        is_new_user = not self.pk 
        # to avoid duplicate rows, must get user to not update photo if the same
        original_user = User.objects.filter(pk=self.pk).first() if not is_new_user else None 
        super().save(*args, **kwargs) 

        # user is new or updated their profile without keeping the same profile photo
        if is_new_user or (self.profile_photo != original_user.profile_photo):
            if self.profile_photo:
                # resizing photo
                SIZE = (500, 500)

                image = Image.open(self.profile_photo.path)
                profile_photo = image.resize(SIZE)
                profile_photo.save(self.profile_photo.path)

                if settings.MEDIA_ROOT + '/app/default-user.png' != self.profile_photo:
                    ProfilePhotos.objects.create(user=self, photo=self.profile_photo)

    def like_post(self, post):
        """
        Liking a post; pass in the post object to be liked by the 
        current user. All important DB operations are handled.
        """
        like, created = Like.objects.get_or_create(user=self, post=post)
        if created:
            post.likes += 1
            post.save()
        return like
    
    def unlike_post(self, post):
        """
        Unliking a post; pass in the post object to be liked by the 
        current user. All important DB operations are handled.
        """
        try:
            like = Like.objects.get(user=self, post=post)
            like.delete()
            post.likes -= 1
            post.save()
        except Like.DoesNotExist:
            return "You haven't liked this post to unlike it."
        
    def accept_friend(self, friend):
        """
        Accepting a friend; pass in the user object to be added as a friend to 
        the current user. All important DB operations are handled.
        """
        try:
            friend_request = FriendRequest.objects.get(user=friend, recipient=self)
            if friend_request.status == "pending":
                existing_friendship, new_friendship = Friendship.objects.get_or_create(user=self, friend=friend)
                if new_friendship:
                    # reciprocal friendship
                    Friendship.objects.create(user=friend, friend=self)
                    friend_request.delete()
                    return (new_friendship, "new")
                return (existing_friendship, "existing")
        except FriendRequest.DoesNotExist:
            return f"No friend request was received from {friend}"
    
    def remove_friend(self, friend):
        """
        Removing a friend; pass in the user object to be removed from the current 
        user's friends list. All important DB operations are handled.
        """
        try:
            remover = Friendship.objects.get(user=self, friend=friend)
            removed = Friendship.objects.get(user=friend, friend=self)
            remover.delete()
            removed.delete()
        except Friendship.DoesNotExist:
            return f"You aren't friend with {friend}."


class ProfilePhotos(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE
    )
    photo = models.ImageField(
        upload_to='profile_photos/',
        blank=False,
        null=False,
    )
    upload_date = models.DateTimeField(
        auto_now_add=True
    )


class ActiveUser(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    is_online = models.BooleanField(
        blank=False,
        null=False,
        default=False
    )
    last_seen = models.DateTimeField(
        auto_now=True
    )