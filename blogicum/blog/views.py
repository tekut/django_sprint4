from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from blog.models import Category, Post, Comment
from blog.constants import POSTS_NUMBER_LIMIT, PAGINATOR_VALUE, PAGE_NUMBER
from django.db.models import Count, Prefetch

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from django.views.generic import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy, reverse

from blog.forms import PostForm, UserForm, CommentForm


@login_required
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
        comment_count=Count('comment')
        )[:POSTS_NUMBER_LIMIT]

    paginator = Paginator(post_list, PAGINATOR_VALUE)
    page_number = request.GET.get(PAGE_NUMBER)
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


@login_required
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
        'comment': Comment.objects.filter(post_id=id),
        }
    return render(request, 'blog/detail.html', context)


@login_required
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
        comment_count=Count("comment")
        )
    paginator = Paginator(post_list, PAGINATOR_VALUE)
    page_number = request.GET.get(PAGE_NUMBER)
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, 'blog/category.html', context)


def get_profile(request, username_slug):
    if request.user.username == username_slug:
        queryset = Post.objects.select_related(
            'location',
            'author',
            'category',
            )
    else:
        None
    user = get_object_or_404(
        User.objects.prefetch_related(
            Prefetch('post_user', queryset.order_by('-pub_date').annotate(comment_count=Count('comment')),),
                ).filter(username=username_slug)
    )
    post_list = user.post_user.all()
    paginator = Paginator(post_list, PAGINATOR_VALUE)
    page_number = request.GET.get(PAGE_NUMBER)
    page_obj = paginator.get_page(page_number)
    context = {'profile': user, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_data
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'id': self.kwargs['pk']})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.object}
        return context

    def get_success_url(self):
        username = self.request.user
        return reverse_lazy('blog:profile', kwargs={'username': username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        comment = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.author = self.request.user
        form.instance.post = comment
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'id': self.kwargs['pk']})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs['pk'])
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', comment.post_id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'id': self.kwargs['post_id']}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs['pk'])
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', comment.post_id)
        return super().dispatch(request, *args, **kwargs)
