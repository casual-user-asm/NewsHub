from django.urls import path

from .views import detail, index


urlpatterns = [
    path('', index, name='index'),
    path('detail/<str:item>/', detail, name='detail'),
]
