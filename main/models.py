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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    author_page_link = models.URLField(max_length=500, blank=True, verbose_name="Ссылка на страницу автора")
    litnet_link = models.URLField(max_length=500, blank=True, verbose_name="Страница автора на Литнет")
    vk_link = models.URLField(max_length=500, blank=True, verbose_name="Страница автора VK")
    subscribers_count = models.PositiveIntegerField(null=True, blank=True, verbose_name="Количество подписчиков")
    genres = models.CharField(max_length=50, choices=GENRE_CHOICES, blank=True, verbose_name="Жанры автора")
    telegram_nickname = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class BlogRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_name = models.CharField(max_length=255)
    litnet_link = models.URLField(max_length=500, verbose_name="Страница автора на Литнет")
    vk_link = models.URLField(max_length=500, verbose_name="Страница автора VK")
    start_date = models.DateField(verbose_name="Дата старта")
    available_from = models.DateField(verbose_name="Можно начать с")
    available_to = models.DateField(verbose_name="Можно закончить по")
    date_created = models.DateField(auto_now_add=True)

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