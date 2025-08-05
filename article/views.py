import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Category, Post, Comment, Rating
from .utils import check_read_articles
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Tizimga muvaffaqiyatli kirdingiz.")
            return redirect('blog:home')  
        else:
            messages.error(request, "Login yoki parol notogri.")
            return redirect('login')

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect('login')

@login_required
def blog_home(request):
    posts = Post.objects.all().order_by('-id')
    paginator = Paginator(posts, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})

def send_verification_code(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            code = random.randint(100000, 999999)
            request.session['verification_code'] = str(code)
            request.session['user_email'] = email

            send_mail(
                subject='Tasdiqlash kodi',
                message=f"Sizning tasdiqlash kodingiz: {code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False
            )

            messages.success(request, "Tasdiqlash kodi emailga yuborildi.")
            return redirect('blog:verify_code') 
        else:
            messages.error(request, "Email manzilingizni kiriting.")
    
    return render(request, 'send_code.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ushbu username band!")
            return redirect('blog:signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Ushbu email band!")
            return redirect('blog:signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False  
        user.save()

        code = random.randint(100000, 999999)
        request.session['verification_code'] = str(code)
        request.session['temp_user_id'] = user.id  

        send_mail(
            subject='Ro‘yxatdan o‘tish — tasdiqlash kodi',
            message=f"Tasdiqlash kodi: {code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )

        messages.success(request, "Emailga tasdiqlash kodi yuborildi.")
        return redirect('blog:verify_code')

    return render(request, 'signup.html')

def verify_code(request):
    if request.method == 'POST':
        user_code = request.POST.get('code')
        session_code = request.session.get('verification_code')
        user_id = request.session.get('temp_user_id')

        if user_code == session_code and user_id:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()

            login(request, user)
            del request.session['verification_code']
            del request.session['temp_user_id']

            messages.success(request, "Royxatdan otish muvaffaqiyatli yakunlandi.")
            return redirect('blog:home')
        else:
            messages.error(request, "Kod notogri!")

    return render(request, 'verify_code.html')

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