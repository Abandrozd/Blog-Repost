from django.db import models
from django.contrib.auth.models import User

# This model extends Django's built-in User model to add extra fields.

GROUPSIZE_CHOICES = [
    ('size1', '<100'),
    ('size2', '100-500'),
    ('size3', '500-1000'),
    ('size4', '>1000'),
]

GENRE_CHOICES = [
    ('genre1', 'Жанр 1'),
    ('genre2', 'Жанр 2'),
    ('genre3', 'Жанр 3'),
    ('genre4', 'Жанр 4'),
]

class UserProfile(models.Model):
    """
    Stores additional information for each user.
    Each UserProfile is linked to a single User instance.
    """

    # This creates a one-to-opyne link with Django's existing User model.
    # on_delete=models.CASCADE means if a User is deleted, their profile is deleted too.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    author_page_link = models.URLField(max_length=500, blank=True, verbose_name="Ссылка на страницу автора")
    groupsize = models.CharField(max_length=10, choices=GROUPSIZE_CHOICES, blank=True, null=True)
    genre = models.CharField(max_length=10, choices=GENRE_CHOICES, blank=True, null=True)

    # This is the extra field you wanted for the Telegram nickname.
    # max_length is required for CharField.
    # blank=True makes this field optional, so users don't have to provide it.
    telegram_nickname = models.CharField(max_length=100, blank=True)

    # This function defines what will be displayed in the Django admin panel.
    def __str__(self):
        return f"{self.user.username}'s Profile"

class BlogRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_name = models.CharField(max_length=255)
    date_created = models.DateField(auto_now_add=True)  # usually auto_now_add date of creation
    date_exchange = models.DateField()

    def __str__(self):
        return self.book_name

class SavedRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_requests')
    request = models.ForeignKey('BlogRequest', on_delete=models.CASCADE, related_name='saves')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'request'],
                name='unique_save_per_user_request'
            )
        ]