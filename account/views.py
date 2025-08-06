import time
import random
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from .forms import SignUpForm, LoginForm , ChangePassForm , ResetPassForm , CustomChangePasswordForm , AuthenticationForm
from django.contrib.auth.decorators import login_required
from .utils import send_to_mail , generate_code
from django.contrib.auth.models import User

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ro‘yxatdan o‘tdingiz')
            return redirect('login')
        else:
            messages.error(request, 'Formada xatolik bor')
    else:
        form = SignUpForm()
    return render(request, 'account/signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Kirish muvafaqiyatli')
            return redirect('blog:home')
        else:
            messages.error(request, 'Login yoki parol xato')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.warning(request, 'Hisobdan chiqdingiz')
    return redirect('blog:home')


@login_required(login_url='login')
def profile_update_view(request):
    user = request.user
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        if not username:
            messages.error(request, "Username bo‘sh bo‘lishi mumkin emas!")
            return redirect('profile-update')

        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        messages.success(request, "Profil ma'lumotlari yangilandi!")
        return redirect('blog:profile')

    return render(request, 'account/edit_profile.html', {'user': user})

@login_required(login_url='login')
def change_pass_view(request):
    if request.method == "GET":
        code = generate_code()
        request.session['verification_code'] = code
        send_to_mail(request.user.email, code)
        messages.info(request, 'Tasdiqlash kodi emailingizga yuborildi.')
        form = ChangePassForm()
        return render(request, 'account/change_password.html', {'form': form})

    else:
        form = ChangePassForm(request.POST)
        if form.is_valid():
            old_pass = form.cleaned_data['old_pass']
            new_pass = form.cleaned_data['new_pass']
            code = form.cleaned_data['code']
            session_code = request.session.get('verification_code')

            if not request.user.check_password(old_pass):
                messages.error(request, 'Eski parol noto‘g‘ri!')
                return redirect('change-pass')

            if session_code != code:
                messages.error(request, 'Tasdiqlash kodi noto‘g‘ri!')
                return redirect('change-pass')

            user = request.user
            user.set_password(new_pass)
            user.save()
            messages.success(request, 'Parol muvaffaqiyatli o‘zgartirildi.')
            return redirect('blog:profile')

        return render(request, 'account/change_password.html', {'form': form})

def reset_pass(request):
    if request.method =="POST":
        try:
            username = request.POST.get('username')
            user = User.objects.get(username=username)
            code = generate_code()
            request.session['reset_code'] = code
            request.session['username'] = username
            send_to_mail(user.email , code)
            return redirect('reset2')

        except User.DoesNotExist:
            messages.info(request , 'Bunday foydalanuvchi topilmadi !')
            return render(request, 'account/reset1.html')

    return render(request , 'account/reset1.html')

def reset2(request):
    if request.method == "POST":
        form = ResetPassForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            code = form.cleaned_data['code']
            session_code = request.session.get('reset_code')
            username = request.session.get('username')

            if session_code != code:
                messages.error(request, 'Tasdiqlash kodi noto‘g‘ri!')
                return redirect('reset2')

            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            messages.success(request, 'Parol muvaffaqiyatli o‘zgartirildi.')
            del request.session['reset_code']
            del request.session['username']
            return redirect('login')
    else:
        form = ResetPassForm()

    return render(request, 'account/reset2.html', {'form': form})

@login_required
def send_code_view(request):
    if request.method == 'POST':
        code = str(random.randint(100000, 999999))
        request.session['email_code'] = code
        request.session['code_time'] = time.time()
        send_to_mail(request.user.email, code)

        messages.success(request, "Tasdiqlash kodi emailingizga yuborildi!")
        return redirect('verify-code')
    return redirect('change-pass')

@login_required
def verify_code_view(request):
    if request.method == 'POST':
        form = CustomChangePasswordForm(request.POST)
        if form.is_valid():
            old_pass = form.cleaned_data['old_password']
            new_pass = form.cleaned_data['new_password1']
            code = form.cleaned_data['code']
            saved_code = request.session.get('email_code')
            code_time = request.session.get('code_time', 0)

            if not saved_code or time.time() - code_time > 600:
                messages.error(request, "Kod eskirgan!")
                return redirect('send-code')

            if code != saved_code:
                messages.error(request, "Noto'g'ri kod kiritildi!")
                return redirect('verify-code')

            if not request.user.check_password(old_pass):
                messages.error(request, "Hozirgi parol noto'g'ri!")
                return redirect('verify-code')

            request.user.set_password(new_pass)
            request.user.save()
            update_session_auth_hash(request, request.user)
            del request.session['email_code']
            del request.session['code_time']

            messages.success(request, "Parol muvaffaqiyatli o'zgartirildi!")
        return redirect('blog:profile')

    return render(request, 'account/verify_code.html', {'form': CustomChangePasswordForm()})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        return redirect('send-code')
    return render(request, 'account/change_password.html')