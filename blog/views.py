from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count

from .forms import CommentForm
from .models import Post, Category, PostForm, Comment, DeletePostForm, DeleteCommentForm
from .constants import PAGINATE_BY


def filter_published_posts(posts, user=None):
    if user and user.is_authenticated:
        return posts.select_related('author', 'location', 'category').filter(
            models.Q(is_published=True, category__is_published=True, pub_date__lte=timezone.now()) |
            models.Q(author=user)
        )
    return posts.select_related('author', 'location', 'category').filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


def index(request):
    """
    Главная страница.
    """
    posts = Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    paginator = Paginator(posts, PAGINATE_BY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, id):
    """
    Страница просмотра поста.
    """
    post = get_object_or_404(
        filter_published_posts(Post.objects, user=request.user),
        id=id
    )

    comments = post.comments.all()

    return render(request, 'blog/detail.html', {
        'post': post,
        'form': CommentForm(),
        'comments': comments,
    })


def category_posts(request, category_slug):
    """
    Страница категории. Показывает список постов, принадлежащих категории.
    """
    category = get_object_or_404(Category, slug=category_slug, is_published=True)
    post_list = filter_published_posts(category.posts.all())
    paginator = Paginator(post_list, PAGINATE_BY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/category.html',
                  {'category': category, 'page_obj': page_obj})


@login_required
def create_post(request):
    """
    Страница для создания нового поста.
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, id):
    """
    Страница для редактирования поста.
    """
    post = get_object_or_404(Post, id=id)
    if post.author != request.user:
        return redirect('blog:post_detail', id=post.id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html',
                  {'form': form, 'is_edit': True})


def profile(request, username):
    """
    Страница профиля пользователя.
    """
    profile = get_object_or_404(User, username=username)

    if request.user == profile:
        post_list = profile.posts.all()
    else:
        post_list = filter_published_posts(profile.posts.all())

    post_list = post_list.annotate(comment_count=Count('comments')).order_by('-pub_date')

    paginator = Paginator(post_list, PAGINATE_BY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/profile.html',
                  {'profile': profile, 'page_obj': page_obj})


def registration(request):
    """
    Страница регистрации нового пользователя.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog:index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration_form.html',
                  {'form': form})


@login_required
def add_comment(request, post_id):
    """
    Добавление комментария к посту.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = CommentForm()
    return render(request, 'blog/comment.html',
                  {'post': post, 'form': form})


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment.html', {
        'post': post,
        'form': form,
        'comment': comment,
        'post_id': post_id,
        'comment_id': comment_id
    })


@login_required
def edit_profile(request):
    """
    Редактирование профиля пользователя.
    """
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'blog/user.html', {'form': form})


@login_required
def delete_post(request, id):
    """Удаление поста."""
    post = get_object_or_404(Post, id=id, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    form = DeletePostForm(request.POST)
    return render(request, 'blog/detail.html',
                  {'post': post, 'form': form})


@login_required
def delete_comment(request, post_id, comment_id):
    """
    Удаление комментария.
    """
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)
    form = DeleteCommentForm()
    return render(request, 'blog/comment.html',
                  {'comment': comment})


@login_required
def user_posts_view(request):
    posts = Post.objects.filter(author=request.user)
    return render(request, 'blog/user.html',
                  {'posts': posts})
