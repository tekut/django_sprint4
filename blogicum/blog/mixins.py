from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from blog.models import Post, Comment
from blog.forms import PostForm


class PostFormValidMixin(LoginRequiredMixin,):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDispatchMixin():
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class CommentDispatchMixin():
    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', self.get_object().post_id)
        return super().dispatch(request, *args, **kwargs)
