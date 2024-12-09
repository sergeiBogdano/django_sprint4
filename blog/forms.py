from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Post, User


class UserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)


class DeletePostForm(forms.Form):
    confirm = forms.BooleanField(required=True,
                                 label='Я подтверждаю удаление поста')


class DeleteCommentForm(forms.Form):
    confirm = forms.BooleanField(required=True,
                                 label='Я подтверждаю удаление комментария')