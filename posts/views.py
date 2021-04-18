from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from yatube.settings import paginator_count
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, paginator_count)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, paginator_count)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'page': page, 'group': group})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('index')
    else:
        form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    following_flag = 'NoneUser'
    username = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=username)
    posts_count = Post.objects.filter(author=username).count()
    paginator = Paginator(posts, paginator_count)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    follower_count = username.follower.count()
    following_count = username.following.count()
    if request.user.is_authenticated:
        following_flag = Follow.objects.filter(user=request.user,
                                               author=username).exists()
    return render(request, 'profile.html',
                  {'username': username,
                   'posts_count': posts_count,
                   'page': page,
                   'follower': follower_count,
                   'following': following_count,
                   'following_flag': following_flag})


def post_view(request, username, post_id):
    following_flag = 'NoneUser'
    username = get_object_or_404(User, username=username)
    post = Post.objects.get(id=post_id)
    posts_count = Post.objects.filter(author=username).count()
    comments = post.comments.all()
    paginator = Paginator(comments, 4)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    form = CommentForm(request.POST or None)
    follower_count = username.follower.count()
    following_count = username.following.count()
    if request.user.is_authenticated:
        following_flag = Follow.objects.filter(user=request.user,
                                               author=username).exists()
    return render(request, 'post.html',
                  {'username': username,
                   'post': post,
                   'posts_count': posts_count,
                   'page': page,
                   'form': form,
                   'comment_context': comments,
                   'follower': follower_count,
                   'following': following_count,
                   'following_flag': following_flag})


@login_required
def post_edit(request, username, post_id):
    username = get_object_or_404(User, username=username)
    if request.user == username:
        post = Post.objects.get(author=username, id=post_id)
        form = PostForm(files=request.FILES or None, instance=post)
        if request.method == 'POST':
            form = PostForm(request.POST, files=request.FILES or None,
                            instance=post)
            if form.is_valid():
                form = form.save(commit=False)
                form.save()
            return redirect('post', username, post.id)
        return render(request, 'new_post.html', {'form': form, 'post': post})
    return HttpResponseForbidden()


@login_required
def post_delete(request, username, post_id):
    username = get_object_or_404(User, username=username)
    if request.user == username:
        post = Post.objects.get(author=username, id=post_id)
        if request.method == 'GET':
            post.delete()
            return redirect('profile', username)
    return HttpResponseForbidden()


@login_required
def add_comment(request, username, post_id):
    username = get_object_or_404(User, username=username)
    post = Post.objects.get(author=username, id=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form = form.save(commit=False)
        form.post = post
        form.author = request.user
        form.save()
        return redirect('post', username, post.id)
    return redirect('post', username, post.id)


@login_required
def follow_index(request):
    latest = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(latest, paginator_count)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if not Follow.objects.filter(user=request.user, author=author).exists():
        if request.user != author:
            Follow.objects.create(user=request.user, author=author)
        return redirect('profile', username)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    if request.user != author:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username)


def page_not_found(request, exception):
    return render(
        request, 'misc/404.html',
        {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
