from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from blog.models import Category, Post
from blog.constants import POSTS_NUMBER_LIMIT


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
