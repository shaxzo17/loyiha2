import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Category, Post, Comment, Rating
from .utils import check_read_articles
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

def home_page(request):
    categories = Category.objects.all()
    posts = Post.objects.all()
    paginator = Paginator(posts, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    last_comments = Comment.objects.all().order_by("-id")[:10]

    data = {
        "categories": categories,
        "page_obj": page_obj,
        "last_comments": last_comments
    }
    return render(request=request, template_name='index.html', context=data)


def detail(request, post_id):
    categories = Category.objects.all()
    post = Post.objects.get(id=post_id)
    category = Category.objects.get(id=post.category.id)
    related_posts = Post.objects.filter(category=category).exclude(id__in=[0, post.id]).order_by("?")

    request.session.modified = True

    if post.id in check_read_articles(request):
        pass
    else:
        check_read_articles(request).append(post.id)
        post.views += 1
        post.save()

    if request.method == 'POST':
        name = request.POST.get("name")
        comment = request.POST.get("comment")
        if all([name, comment]):
            Comment.objects.create(
                author=name,
                comment=comment,
                post=post
            )
            messages.add_message(request, messages.SUCCESS, "Successfuly !")
        else:
            messages.add_message(request, messages.ERROR, "Wrong !")

    return render(request, "detail.html", context={
        "post": post,
        "categories": categories,
        "related_posts": related_posts})


def set_rating(request, value, post_id):
    post = Post.objects.get(id=post_id)
    value = int(value)
    # print(post, value)
    if all([post, value]):
        Rating.objects.create(
            post=post,
            value=value
        )
        messages.add_message(request, messages.SUCCESS, "Rating set")
    else:
        messages.add_message(request, messages.WARNING, "Rating not set")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def category_list(request, category_slug):
    category = Category.objects.get(slug=category_slug)
    posts = Post.objects.filter(category=category)
    last_comments = Comment.objects.all().order_by("-id")[:10]

    paginator = Paginator(posts, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "index.html", context={"page_obj": page_obj, "last_comments": last_comments})


def search(request):
    query = request.GET.get('q')
    if query:
        results = Post.objects.filter(title__icontains=query)
    else:
        results = Post.objects.none()

    paginator = Paginator(results, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'index.html', {'page_obj': page_obj, 'query': query})





def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        send_mail(
            f"Contact Form: {subject}",
            f"From: {name} <{email}>\n\n{message}",
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL],
            fail_silently=False,
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect('blog:contact')

    return render(request, 'contact.html')


@login_required(login_url='login')
def profile_view(request):
    return render(request, 'account/profile.html', {'user': request.user})

@login_required(login_url='login')
def update_profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        image = request.FILES.get('image')

        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, "Bu username allaqachon band.")
            return redirect('blog:update-profile')

        user.username = username
        user.email = email
        user.save()

        if image:
            profile.image = image
            profile.save()

        messages.success(request, "Profil muvaffaqiyatli yangilandi.")
        return redirect('blog:profile')

    return render(request, 'account/edit_profile.html', {
        'user': user,
        'profile': profile
    })

@login_required(login_url='login')
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Parolingiz muvaffaqiyatli o'zgartirildi!")
            return redirect('blog:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if 'old_password' in field:
                        messages.error(request, "Hozirgi parolingiz xato kiritildi!")
                    elif 'new_password2' in field:
                        messages.error(request, "Yangi parollar mos kelmadi!")
                    else:
                        messages.error(request, f"Xato: {error}")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'account/change_password.html')
def about(request):
    return render(request , 'account/about.html')