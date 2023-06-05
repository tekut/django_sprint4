import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from django.views.generic import (
    CreateView, DeleteView, UpdateView
)
from django.urls import reverse_lazy

from django.shortcuts import render, get_object_or_404, redirect, render
from django.utils import timezone

from blog.forms import PostForm, UserForm
from blog.models import Category, Post, Tag
from blog.constants import POSTS_NUMBER_LIMIT

from django.views.generic import TemplateView

from django.http import HttpResponse


@login_required
def simple_view(request):
    return HttpResponse('Страница для залогиненных пользователей!')


def index(request):
    post_list = Post.objects.select_related(
        'category',
        'location',
        'author',
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )[:POSTS_NUMBER_LIMIT]
    context = {'post_list': post_list}
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    post_list = get_object_or_404(
        Post.objects.select_related(
            'location', 'author', 'category').
        filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        ),
        pk=id,
    )
    context = {'post': post_list}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category.objects.filter(
            slug=category_slug,
            is_published=True,
        )
    )
    post_list = category.post.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
    )
    context = {'post_list': post_list, 'category': category}
    return render(request, 'blog/category.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "blog/user.html"
    form_class = UserForm
    success_url = reverse_lazy("blog:index")
