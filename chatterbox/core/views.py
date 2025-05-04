# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count
from .models import Post, Comment, Category, User
from .forms import RegisterForm, LoginForm, PostForm, CommentForm, CustomPasswordResetForm, CustomSetPasswordForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.db.models import Q
from django.http import JsonResponse
from django.db.models import Count
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse

def post_autocomplete(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    
    posts = Post.objects.filter(category_id=category_id)
    
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )[:10]
    
    results = [{
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author.username
    } for post in posts]
    
    return JsonResponse({'results': results})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    
    # Get search query if exists
    search_query = request.GET.get('q', '')
    
    # Base queryset filtered by category
    posts = Post.objects.filter(category=category)
    
    # Apply search filter if query exists
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(posts.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/category_detail.html', {
        'category': category,
        'page_obj': page_obj,
        'search_query': search_query
    })

def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    # example context - add more if needed
    context = {
        'profile_user': profile_user,
    }
    return render(request, 'core/profile.html', context)

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'core/password_change.html'  # Your custom template if needed

    def form_valid(self, form):
        messages.success(self.request, "Your password was changed successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Custom error message handling
        if form.errors.get('new_password1'):
            for error in form.errors['new_password1']:
                if 'too common' in error:
                    messages.error(self.request, "Your password is too common. Please choose a stronger one.")
                if 'entirely numeric' in error:
                    messages.error(self.request, "Your password can't be entirely numeric.")
        
        # Return the form with errors to stay in the modal
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('user_profile', kwargs={'username': self.request.user.username})

def category_list(request):
    category = Category.objects.annotate(post_count=Count('post')).all()
    return render(request, 'category_detail.html', {'category': category})

def category_autocomplete(request):
    query = request.GET.get('q', '')
    results = Category.objects.filter(name__icontains=query).annotate(
        post_count=Count('post')
    )[:10]
    
    data = [{
        'name': cat.name,
        'slug': cat.slug,
        'post_count': cat.post_count
    } for cat in results]
    
    return JsonResponse({'results': data})

def search_autocomplete(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        )[:5]
        results = [{
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'category': post.category.name,
            'author': post.author.username
        } for post in posts]
    return JsonResponse({'results': results})

def search_view(request):
    query = request.GET.get('q', '')
    posts = Post.objects.all()
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        ).order_by('-created_at')
    return render(request, 'core/search_results.html', {'posts': posts, 'query': query})

def user_profile(request, username):
    User = get_user_model()
    profile_user = get_object_or_404(User, username=username)
    
    context = {
        'profile_user': profile_user,
        'user_posts': Post.objects.filter(author=profile_user).order_by('-created_at')[:5],
        'user_comments': Comment.objects.filter(author=profile_user).order_by('-created_at')[:5],
        'post_count': Post.objects.filter(author=profile_user).count(),
        'comment_count': Comment.objects.filter(author=profile_user).count(),
    }
    return render(request, 'core/profile.html', context)

@login_required
def reply_comment(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = parent_comment.post
            reply.author = request.user
            reply.parent = parent_comment
            reply.save()
            return redirect('post_detail', pk=parent_comment.post.id)
    else:
        form = CommentForm()
    
    context = {
        'form': form,
        'parent_comment': parent_comment,
    }
    return render(request, 'core/reply_comment.html', context)

def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Check if the current user is the author
    if request.user != post.author:
        messages.error(request, "You don't have permission to edit this post!")
        return redirect('post_detail', pk=post.pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'core/post_form.html', {
        'form': form,
        'action': 'Edit'
    })

@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # Check if the current user is the author
    if request.user != comment.author:
        messages.error(request, "You don't have permission to edit this comment!")
        return redirect('post_detail', pk=comment.post.pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated successfully!')
            return redirect('post_detail', post_id=comment.post.pk)
    else:
        form = CommentForm(instance=comment)
    
    context = {
        'form': form,
        'comment': comment,
        'action': 'Edit'
    }
    return render(request, 'core/comment_form.html', context)

def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_id = comment.post.id
    
    # Check permissions
    if not (request.user == comment.author or request.user.is_staff):
        messages.error(request, "You don't have permission to delete this comment!")
        return redirect('post_detail', post_id=post_id)
    
    if request.method == 'POST':
        try:
            parent_comment_id = comment.parent.id if comment.parent else None
            comment.delete()
            messages.success(request, "Comment deleted successfully!")
            
            # Fixed redirect with fragment
            if parent_comment_id:
                url = reverse('post_detail', kwargs={'post_id': post_id}) + f'#comment-{parent_comment_id}'
                return HttpResponseRedirect(url)
            return redirect('post_detail', post_id=post_id)
            
        except Exception as e:
            messages.error(request, f"Error deleting comment: {str(e)}")
            return redirect('post_detail', post_id=post_id)
    
    # GET request - show confirmation page
    return render(request, 'core/comment_confirm_delete.html', {
        'comment': comment,
        'post': comment.post,
    })

def edit_post(request, pk):
    # Get the post or return 404
    post = get_object_or_404(Post, pk=pk)
    
    # Check if the current user is the author
    if request.user != post.author:
        messages.error(request, "You don't have permission to edit this post!")
        return redirect('post_detail', pk=post.pk)
    
    if request.method == 'POST':
        # Process the form data
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', pk=post.pk)
    else:
        # Display the form with current post data
        form = PostForm(instance=post)
    
    return render(request, 'core/post_form.html', {
        'form': form,
        'action': 'Edit'
    })

def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user != post.author:
        messages.error(request, "You don't have permission to delete this post!")
        return redirect('post_detail', post_id=post.pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect('home')
    
    # GET request - show confirmation page
    return render(request, 'core/post_confirm_delete.html', {'post': post})

def home(request):
    categories = Category.objects.annotate(post_count=Count('post')).order_by('-post_count')
    posts = Post.objects.select_related('author', 'category').prefetch_related('upvotes', 'downvotes').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'page_obj': page_obj,
    }
    return render(request, 'core/home.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category).order_by('-created_at')
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'core/category_detail.html', context)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not form.cleaned_data['remember_me']:
                request.session.set_expiry(0)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def create_post(request):
    if not request.user.can_post():
        messages.warning(request, 'You are posting too frequently. Please wait 5 minutes between posts.')
        return redirect('home')
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            
            # Update user's last post time
            request.user.last_post_time = timezone.now()
            request.user.save()
            
            messages.success(request, 'Your post has been created!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm()
    
    return render(request, 'core/post_form.html', {'form': form, 'action': 'Create'})

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post, parent=None).order_by('-created_at')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'You need to login to comment.')
            return redirect('login')
        
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been posted!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'core/post_detail.html', context)

@login_required
def reply_comment(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = parent_comment.post
            comment.author = request.user
            comment.parent = parent_comment
            comment.save()
            messages.success(request, 'Your reply has been posted!')
            return redirect('post_detail', post_id=parent_comment.post.id)
    else:
        form = CommentForm()
    
    context = {
        'parent_comment': parent_comment,
        'form': form,
    }
    return render(request, 'core/reply_comment.html', context)

@login_required
def vote_post(request, post_id, vote_type):
    post = get_object_or_404(Post, id=post_id)
    
    if post.author == request.user:
        messages.warning(request, "You can't react on your own post!")
        return redirect('post_detail', post_id=post.id)
    
    if vote_type == 'up':
        if request.user in post.downvotes.all():
            post.downvotes.remove(request.user)
        post.upvotes.add(request.user)
        messages.success(request, "You like the post.")
    elif vote_type == 'down':
        if request.user in post.upvotes.all():
            post.upvotes.remove(request.user)
        post.downvotes.add(request.user)
        messages.success(request, "You dislike the post.")
    
    # Check for spam behavior
    if post.vote_score() < -3:
        post.author.is_spammer = True
        post.author.save()
        messages.warning(request, f"User {post.author.username} has been marked as a spammer due to excessive downvotes.")
    
    return redirect('post_detail', post_id=post.id)

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'core/password_reset.html'
    email_template_name = 'core/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'core/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')