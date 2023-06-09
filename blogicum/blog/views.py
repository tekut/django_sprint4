from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from blog.mixins import (
    CommentDispatchMixin,
    PostDispatchMixin,
    PostFormValidMixin,
)
from blog.models import Category, Comment, Post
from blog.forms import CommentForm, PostForm, UserForm
from blog.constants import POSTS_NUMBER_LIMIT, PAGE_NUMBER


def index(request):
    post_list = Post.objects.select_related(
        'location',
        'author',
        'category',
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).order_by(
        '-pub_date',
    ).annotate(
        comment_count=Count('comment'),
    )

    paginator = Paginator(post_list, POSTS_NUMBER_LIMIT)
    page_number = request.GET.get(PAGE_NUMBER)
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    post_list = get_object_or_404(
        Post.objects.select_related(
            'location',
            'author',
            'category',
        ).filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        ),
        pk=id,
    )
    context = {
        'post': post_list,
        'form': CommentForm(),
        'comments': Comment.objects.filter(post_id=id),
    }
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
    ).order_by(
        '-pub_date',
    ).annotate(
        comment_count=Count('comment'),
    )
    paginator = Paginator(post_list, POSTS_NUMBER_LIMIT)
    page_number = request.GET.get(PAGE_NUMBER)
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, 'blog/category.html', context)


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    ordering = 'id'
    paginate_by = POSTS_NUMBER_LIMIT

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs.get('username'),
        )
        return context

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs.get('username'))
        result = author.post.annotate(
            comment_count=Count('comment'),
        ).order_by('-pub_date')
        return result


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', args=[username])


class PostCreateView(PostFormValidMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', args=[username])


class PostUpdateView(PostFormValidMixin, PostDispatchMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['pk']])


class PostDeleteView(LoginRequiredMixin, PostDispatchMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        context = dict(
            **super().get_context_data(**kwargs),
            form={'instance': self.object},
            comments=self.object.comment.all(),
        )
        return context

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        comment = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.author = self.request.user
        form.instance.post = comment
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['pk']])


class CommentUpdateView(LoginRequiredMixin, CommentDispatchMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail', args=[self.kwargs['post_id']]
        )


class CommentDeleteView(LoginRequiredMixin, CommentDispatchMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail', args=[self.kwargs['post_id']]
        )
