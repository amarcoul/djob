from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'articles', ArticleViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('vue/', incrementer_vue, name='vue'),
    path('likes/', incrementer_likes, name='likes'),
    path('modifie/<int:pk>', modifier_article, name='modifier_article'),
    path('articles/<int:pk>/', article_delete, name='article-delete'),
    path('article/<int:id>/', get_article_by_id, name='article-detail'),
]

