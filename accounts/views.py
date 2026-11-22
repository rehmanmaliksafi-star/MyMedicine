from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

def login_view(request):
    if request.user.is_authenticated: return redirect('home')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username',''), password=request.POST.get('password',''))
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(request.GET.get('next','home'))
        messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.user.is_authenticated: return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        email = request.POST.get('email','').strip()
        first_name = request.POST.get('first_name','').strip()
        last_name = request.POST.get('last_name','').strip()
        password1 = request.POST.get('password1','')
        password2 = request.POST.get('password2','')
        errors = []
        if not username: errors.append('Username is required.')
        elif User.objects.filter(username=username).exists(): errors.append('Username already taken.')
        if not email: errors.append('Email is required.')
        elif User.objects.filter(email=email).exists(): errors.append('Email already registered.')
        if len(password1) < 8: errors.append('Password must be at least 8 characters.')
        if password1 != password2: errors.append('Passwords do not match.')
        if errors:
            for e in errors: messages.error(request, e)
        else:
            user = User.objects.create_user(username=username, email=email, password=password1, first_name=first_name, last_name=last_name)
            login(request, user)
            messages.success(request, f'Welcome to MyMedicine, {first_name or username}!')
            return redirect('home')
    return render(request, 'accounts/register.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out safely.')
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name','').strip()
        request.user.last_name = request.POST.get('last_name','').strip()
        request.user.email = request.POST.get('email','').strip()
        request.user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'accounts/profile.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        old_pass = request.POST.get('old_password')
        new1 = request.POST.get('new_password1')
        new2 = request.POST.get('new_password2')
        if not request.user.check_password(old_pass): messages.error(request, 'Current password is incorrect.')
        elif new1 != new2: messages.error(request, 'New passwords do not match.')
        elif len(new1) < 8: messages.error(request, 'Password must be at least 8 characters.')
        else:
            request.user.set_password(new1); request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed successfully!'); return redirect('profile')
    return render(request, 'accounts/change_password.html')
