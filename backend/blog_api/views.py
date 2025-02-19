from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework import viewsets
from blog_api.serializer import *
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import F
#gestion des utilisateurs
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@api_view(['POST'])
def register(request):
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    email = request.data.get("email")
    password = request.data.get("password")

    print("Données reçues:", first_name, last_name, email, password)  # Log

    if not all([email, password, first_name, last_name]):
        return JsonResponse({"error": "Tous les champs sont requis"}, status=400)

    # Vérifier si l'email existe déjà
    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "L'email est déjà utilisé"}, status=400)

    user = User.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=make_password(password),
    )

    return JsonResponse({"message": "Inscription réussie", "user_id": user.id})

@api_view(['POST'])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if not email or not password:
        return JsonResponse({"error": "Email et mot de passe sont requis"}, status=status.HTTP_400_BAD_REQUEST)
    
    print("Données reçues:", email, password) 
    # Utilisation de authenticate pour valider l'utilisateur
    user = authenticate(request, email=email, password=password)
    print("Utilisateur trouvé:", user)  # Log pour vérifier l'utilisateur

    if user is not None:
        # Création d'un token JWT
        refresh = RefreshToken.for_user(user)
        return JsonResponse(
            {
                "token": str(refresh.access_token),  # Envoi du token
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
            }
        )
    else:
        print("Échec de l'authentification")  # Log pour vérifier l'échec
        return JsonResponse({"error": "Email ou mot de passe incorrect"}, status=400)
#gestion des articles
@api_view(['POST'])
def incrementer_vue(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    article.vue += 1
    article.save()
    return JsonResponse({'nombre de vue': article.vue})

@api_view(['POST'])
def incrementer_likes(request,article_id):
    article = get_object_or_404(Article, id=article_id)
    article.likes += 1
    article.save()
    return JsonResponse({'nombre de likes': article.likes})

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-date_publication')
    serializer_class = ArticleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(categories__nom=category)
        return queryset

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(count=F('nombre_article')).order_by('count')
    serializer_class = CategorySerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

@api_view(['POST'])
def modifier_article(request,pk):
    article= get_object_or_404(Article,pk=pk)

    return JsonResponse({'message': 'Article updated successfully'})

@api_view(['POST'])
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.delete()
    return JsonResponse({'message': 'Article deleted successfully'})

@api_view(['GET'])
def get_article_by_id(request, id):
    article = get_object_or_404(Article, id=id)
    serializer = ArticleSerializer(article)
    return Response(serializer.data, status=status.HTTP_200_OK)