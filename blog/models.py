from django.db import models
from django.contrib.auth import get_user_model
from django import forms

from .constants import MAX_FIELD_LENGTH, MAX_SHORT_STRING_LENGTH

User = get_user_model()


class IsPublishedAbstract(models.Model):
    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True


class CreatedAtAbstract(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Category(IsPublishedAbstract, CreatedAtAbstract):
    title = models.CharField(
        max_length=MAX_FIELD_LENGTH,
        verbose_name='Заголовок'
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:MAX_SHORT_STRING_LENGTH]


class Location(IsPublishedAbstract, CreatedAtAbstract):
    name = models.CharField(
        max_length=MAX_FIELD_LENGTH,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:MAX_SHORT_STRING_LENGTH]


class Post(IsPublishedAbstract, CreatedAtAbstract):
    title = models.CharField(
        max_length=MAX_FIELD_LENGTH,
        verbose_name='Заголовок'
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — можно делать '
                  'отложенные публикации.'
    )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор публикации',
                               related_name='posts')
    location = models.ForeignKey(Location,
                                 on_delete=models.SET_NULL,
                                 verbose_name='Местоположение',
                                 null=True,
                                 related_name='posts')
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 verbose_name='Категория',
                                 related_name='posts')
    image = models.ImageField(
        upload_to='posts/',
        verbose_name='Изображение',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:MAX_SHORT_STRING_LENGTH]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title',
                  'text',
                  'pub_date',
                  'location',
                  'category',
                  'image']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             related_name='comments',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class DeletePostForm(forms.Form):
    confirm = forms.BooleanField(required=True,
                                 label="Я подтверждаю удаление поста")


class DeleteCommentForm(forms.Form):
    confirm = forms.BooleanField(required=True,
                                 label="Я подтверждаю удаление комментария")
