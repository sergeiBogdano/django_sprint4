from django.urls import path
from .views import (
    index, post_detail, create_post, edit_post,
    delete_post, category_posts, add_comment,
    edit_comment, registration, profile, edit_profile,
    user_posts_view, delete_comment
)

app_name = 'blog'

urlpatterns = [
    path('', index, name='index'),
    path('posts/<int:id>/', post_detail, name='post_detail'),
    path('create/', create_post, name='create_post'),
    path('posts/<int:id>/edit/', edit_post, name='edit_post'),
    path('posts/<int:id>/delete/', delete_post, name='delete_post'),
    path('category/<slug:category_slug>/', category_posts, name='category_posts'),
    path('posts/<int:post_id>/comment/', add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', edit_comment, name='edit_comment'),
    path('registration/', registration, name='registration'),
    path('profile/<str:username>/', profile, name='profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('user_posts/', user_posts_view, name='user_posts'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/', delete_comment, name='delete_comment'),
]
