from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .constants import PAGINATE_BY
from .forms import CommentForm, DeletePostForm, PostForm
from .models import Category, Comment, Post


def paginate_queryset(request, queryset, paginate_by):
    paginator = Paginator(queryset, paginate_by)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def annotate_and_order_posts(posts):
    return posts.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def filter_published_posts(posts,
                           apply_filter=True,
                           use_select_related=True):
    if use_select_related:
        posts = posts.select_related('author', 'location', 'category')

    if apply_filter:
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    posts = posts.annotate(comment_count=Count('comments'))

    return posts


def index(request):
    posts = filter_published_posts(Post.objects).annotate(
        comment_count=Count('comments')
    ).order_by(*Post._meta.ordering)

    page_obj = paginate_queryset(request, posts, PAGINATE_BY)

    return render(request, 'blog/index.html',
                  {'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author',
                                                         'location',
                                                         'category'),
                             id=post_id)

    if not post.is_published and post.author != request.user:
        return render(request, 'pages/404.html', status=404)

    comments = post.comments.all()

    return render(request, 'blog/detail.html', {
        'post': post,
        'form': CommentForm(),
        'comments': comments,
    })


def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug,
                                 is_published=True)

    post_list = filter_published_posts(category.posts.all(),
                                       use_select_related=False)

    post_list = annotate_and_order_posts(post_list)

    page_obj = paginate_queryset(request, post_list, PAGINATE_BY)

    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj
    })


@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)

    if not form.is_valid():
        return render(request, 'blog/create.html',
                      {'form': form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('blog:profile', username=request.user.username)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)

    form = PostForm(request.POST or None,
                    request.FILES or None,
                    instance=post)

    if not form.is_valid():
        return render(request, 'blog/create.html',
                      {'form': form, 'is_edit': True})

    form.save()
    return redirect('blog:post_detail', post_id=post.id)


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user:
        post_list = profile_user.posts.all()
    else:
        post_list = filter_published_posts(profile_user.posts.all())

    post_list = annotate_and_order_posts(post_list)

    page_obj = paginate_queryset(request, post_list, PAGINATE_BY)

    return render(request, 'blog/profile.html', {
        'profile': profile_user,
        'page_obj': page_obj
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    form = CommentForm(request.POST or None)

    if not form.is_valid():
        return render(request, 'blog/comment.html',
                      {'post': post, 'form': form})

    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post = get_object_or_404(Post, id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=comment)

    if not form.is_valid():
        return render(request, 'blog/comment.html', {
            'post': post,
            'form': form,
            'comment': comment
        })

    form.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_profile(request):
    form = UserChangeForm(request.POST or None, instance=request.user)
    if not form.is_valid():
        return render(request, 'blog/user.html',
                      {'form': form})
    form.save()
    return redirect('blog:profile', username=request.user.username)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    form = DeletePostForm(request.POST or None)
    return render(request, 'blog/detail.html',
                  {'post': post, 'form': form})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post = get_object_or_404(Post, id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html',
                  {'comment': comment, 'post': post})
