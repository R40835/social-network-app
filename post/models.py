from django.db import models
from django.core.exceptions import ValidationError
from PIL import Image


class Post(models.Model):
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE,
        related_name='posts_created'
    )
    description = models.TextField(
        null=True,
        blank=True,
        max_length=1000,
    )
    photo = models.ImageField(
        upload_to="post_photos/",
        null=True,
        blank=True,
    )
    date_created = models.DateTimeField(
        auto_now_add=True
    )
    likes = models.PositiveIntegerField(
        default=0,
        null=False,
        blank=False
    ) 
    comments = models.ManyToManyField(
        'users.User',
        through='Comment', 
    )
    is_new = models.BooleanField(
        default=True,
        null=False,
        blank=False
    )

    def clean(self):
        """
        Validate that a post has either a description or a photo. 
        Raises a ValidationError if both are missing.
        """
        if not self.description and not self.photo:
            raise ValidationError("A post must have either a description or a photo.")

    def save(self, *args, **kwargs):
        """
        Override the save method to handle post photo resizing.
        """
        self.clean()  # Run the clean method to validate the post
        super().save(*args, **kwargs)

        if self.photo:
            # resizing photo
            SIZE = (500, 500)

            image = Image.open(self.photo.path)
            post_photo = image.resize(SIZE)
            post_photo.save(self.photo.path)


class Like(models.Model):
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE
    )
    date_liked = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        """
        String representation of the object.
        """
        return f"{self.user.id} liked {self.post}"

    class Meta:
        unique_together = ('user', 'post')  # Prevent duplicate likes


class Comment(models.Model):
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE
    )
    text = models.TextField(
        null=False,
        blank=False,
        max_length=1000,
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        """
        String representation of the object.
        """
        return f"Comment by {self.user.id} on {self.post}"
