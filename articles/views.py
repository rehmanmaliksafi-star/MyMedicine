from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Article, UserHealthProfile

def article_list(request):
    articles = Article.objects.filter(is_published=True)
    category = request.GET.get('category','')
    if category: articles = articles.filter(category__icontains=category)
    categories = Article.objects.filter(is_published=True).values_list('category', flat=True).distinct()
    return render(request, 'articles/article_list.html', {'articles': articles, 'categories': categories, 'current_category': category})

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    article.views += 1; article.save(update_fields=['views'])
    return render(request, 'articles/article_detail.html', {'article': article})

@login_required
def health_profile(request):
    profile, _ = UserHealthProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.age = request.POST.get('age') or None
        profile.gender = request.POST.get('gender','')
        profile.medical_conditions = request.POST.get('medical_conditions','')
        profile.allergies = request.POST.get('allergies','')
        profile.save()
        messages.success(request, 'Health profile updated!')
        return redirect('health_profile')
    return render(request, 'articles/health_profile.html', {'profile': profile})
