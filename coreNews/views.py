import os

import django
from django.shortcuts import render

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReadAndGo.settings')
django.setup()
from coreNews.models import News


def index(request):
    news_publisher = News.objects.values_list('publisher', flat=True).distinct()
    return render(request, 'coreNews/index.html', {'data': news_publisher})


def detail(request, item):
    article_data = News.objects.filter(publisher=item)
    return render(request, 'coreNews/detail.html', {'item': article_data})
