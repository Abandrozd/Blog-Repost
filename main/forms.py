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

    vk_link = forms.URLField(
        required=True,
        label="Ссылка на страницу автора в VK",
        help_text="Введите ссылку на вашу страницу автора в VK (например, https://vk.com/yourprofile)."
    )

    litnet_link = forms.URLField(
        required=True,
        label="Ссылка на страницу автора на Литнет",
        help_text="Введите ссылку на Litnet (например, https://litnet.com/ru/yourprofile)"
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
        fields = ("username", "vk_link", "litnet_link", "telegram_nickname", "password1", "password2")
        labels = {
            'username': 'Имя пользователя',
        }
        help_texts = {
            'username': 'Только буквы, цифры и символы @/./+/-/_.',
        }

    def save(self, commit=True):
        user = super().save(commit)
        telegram_nickname = self.cleaned_data['telegram_nickname']
        vk_link = self.cleaned_data['vk_link']  # <-- Fixed here!
        litnet_link = self.cleaned_data['litnet_link']
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'vk_link': vk_link,
                'litnet_link': litnet_link,
                'telegram_nickname': telegram_nickname,
            }
        )
        return user

class BlogRequestForm(forms.ModelForm):
    unavailable_dates = forms.CharField(
        required=False,
        label="Недоступные даты",
        help_text="Выберите даты, когда вы НЕ сможете выполнить запрос по этой заявке.",
        widget=forms.TextInput(attrs={'class': 'unavailable-dates-input', 'autocomplete': 'off'})
    )
    class Meta:
        model = BlogRequest
        fields = ['book_name', 'author_page_link', 'start_date', 'available_from', 'available_to', 'unavailable_dates']
        labels = {
            'book_name': 'Название книги',
            'author_page_link': 'Ссылка на книгу',
            'start_date': 'Дата старта',
            'available_from': 'Свободен с',
            'available_to': 'Свободен по',
            'unavailable_dates': 'Недоступные даты',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'flatpickr-input', 'autocomplete': 'off'}),
            'available_from': forms.DateInput(attrs={'class': 'flatpickr-input', 'autocomplete': 'off'}),
            'available_to': forms.DateInput(attrs={'class': 'flatpickr-input', 'autocomplete': 'off'}),
            'author_page_link': forms.URLInput(attrs={'class': 'form-field', 'placeholder': 'https://...'})
        }

    def clean_unavailable_dates(self):
        raw = self.cleaned_data['unavailable_dates']
        # Split by comma, strip whitespace, validate as dates if needed
        dates = [d.strip() for d in raw.split(',') if d.strip()]
        return dates

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Cleaned unavailable_dates: save as list/JSON
        if isinstance(self.cleaned_data['unavailable_dates'], str):
            dates = [d.strip() for d in self.cleaned_data['unavailable_dates'].split(',') if d.strip()]
        else:
            dates = self.cleaned_data['unavailable_dates']
        instance.unavailable_dates = dates
        if commit:
            instance.save()
        return instance



class ProfileForm(forms.ModelForm):
    subscribers_count = forms.ChoiceField(
        choices=[
            ('size1', '<100'),
            ('size2', '100-500'),
            ('size3', '500-1000'),
            ('size4', '>1000'),
        ],
        required=True,
        label='Размер подписчиков в группе'
    )
    genres = forms.ChoiceField(
        choices=[
            ('genre1', 'Жанр 1'),
            ('genre2', 'Жанр 2'),
            ('genre3', 'Жанр 3'),
            ('genre4', 'Жанр 4'),
        ],
        required=True,
        label='Жанр'
    )

    telegram_nickname = forms.CharField(
        max_length=100,
        required=False,
        label="Телеграм-никнейм",
        help_text="например, @your_nick"
    )

    litnet_link = forms.URLField(
        required=False,
        label='Страница автора на Литнет'
    )
    vk_link = forms.URLField(
        required=False,
        label='Страница автора VK'
    )

    class Meta:
        model = UserProfile
        fields = [
            'author_page_link',
            'subscribers_count',
            'genres',
            'litnet_link',
            'vk_link',
        ]
        labels = {'author_page_link': 'Ссылка на страницу автора',
                  }
        widgets = {

        }