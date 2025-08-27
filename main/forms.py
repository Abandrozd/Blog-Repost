from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, BlogRequest

class CustomUserCreationForm(UserCreationForm):
    telegram_nickname = forms.CharField(
        max_length=100,
        required=False,
        label="Телеграм-никнейм",
        help_text="Укажите ваш никнейм в Telegram (например, @example)."
    )

    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput,
        help_text=(
            "Ваш пароль должен содержать минимум 8 символов, "
            "не должен быть слишком похож на другую вашу личную информацию, "
            "и не должен быть полностью числовым."
        ),
    )

    password2 = forms.CharField(
        label="Подтверждение пароля",
        strip=False,
        widget=forms.PasswordInput,
        help_text="Введите тот же самый пароль для подтверждения.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "telegram_nickname", "password1", "password2")
        labels = {
            'username': 'Имя пользователя',
        }
        help_texts = {
            'username': 'Только буквы, цифры и символы @/./+/-/_.',
        }

    def save(self, commit=True):
        user = super().save(commit)
        telegram_nickname = self.cleaned_data['telegram_nickname']
        UserProfile.objects.update_or_create(
            user=user,
            defaults={'telegram_nickname': telegram_nickname}
        )
        return user

class BlogRequestForm(forms.ModelForm):
    class Meta:
        model = BlogRequest
        fields = ['book_name', 'date_exchange']
        labels = {
            'book_name': 'Название книги:',
            'date_exchange': 'Дата обмена:'
        }
        widgets = {
            'date_exchange': forms.DateInput(attrs={'type': 'date'}),
        }

class ProfileForm(forms.ModelForm):
    groupsize = forms.ChoiceField(
        choices=[
            ('size1', '<100'),
            ('size2', '100-500'),
            ('size3', '500-1000'),
            ('size4', '>1000'),
        ],
        required=True,
        label='Размер подписчиков в группе'
    )
    genre = forms.ChoiceField(
        choices=[
            ('genre1', 'Жанр 1'),
            ('genre2', 'Жанр 2'),
            ('genre3', 'Жанр 3'),
            ('genre4', 'Жанр 4'),
        ],
        required=True,
        label='Жанр'
    )

    class Meta:
        model = UserProfile
        fields = ['author_page_link', 'groupsize', 'genre']
        labels = {'author_page_link': 'Ссылка на страницу автора',
                  }
        widgets = {
            'author_page_link': forms.URLInput(attrs={
                'placeholder': 'Пример: https://example.com',
                'class': 'form-control',
            })
        }