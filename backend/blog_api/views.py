from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework import viewsets
from blog_api.serializer import *
from rest_framework.decorators import api_view,permission_classes
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import F
from rest_framework.permissions import IsAuthenticated

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
                "last_login": user.last_login,
                "is_superuser": user.is_superuser,
                "username": user.username,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
                "date_joined": user.date_joined,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "password": user.password,  
                "date_creation": user.date_creation,  # Champ personnalisé
                "photo_profil": user.photo_profil.url if user.photo_profil else None,  # Champ personnalisé
                "bio": user.bio,  # Champ personnalisé
                "groups": list(user.groups.values_list('name', flat=True)),  # Liste des noms de groupes
                "user_permissions": list(user.user_permissions.values_list('codename', flat=True)), 
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
def incrementer_likes(request, article_id):
    # Utiliser article_id correctement pour obtenir l'article
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

# Ajoutez cette ligne en haut de votre fichier views.py avec les autres importations
import json

# Votre classe ArticleViewSetadmin reste la même, assurez-vous juste que json est importé
class ArticleViewSetadmin(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-date_publication')
    serializer_class = AddArticleSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(categories__nom=category)
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Debug
        print("Données reçues:", request.data)
        
        # Créer une copie mutable des données
        request_data = request.data.copy()
        
        # Correction du problème auteur
        if 'auteur' in request_data and request_data['auteur'] == '[object Object]':
            # Si l'auteur est l'objet original, utiliser l'auteur actuel de l'article
            request_data['auteur'] = instance.auteur.id if instance.auteur else None
        
        # Traitement des catégories
        if 'categories' in request_data:
            categories_data = request_data['categories']
            # Nettoyage des catégories
            if isinstance(categories_data, list):
                cleaned_categories = []
                for cat in categories_data:
                    # Enlever les guillemets supplémentaires s'ils existent
                    if isinstance(cat, str):
                        # Si c'est une chaîne JSON, essayer de la décoder
                        try:
                            # Enlever les guillemets au début et à la fin si nécessaire
                            if cat.startswith('"') and cat.endswith('"'):
                                cat = cat[1:-1]
                            cleaned_categories.append(cat)
                        except:
                            cleaned_categories.append(cat)
                    else:
                        cleaned_categories.append(cat)
                request_data['categories'] = cleaned_categories
            elif isinstance(categories_data, str):
                # Gérer le cas d'une seule catégorie
                try:
                    # Si c'est une chaîne JSON, essayer de la décoder
                    cat_value = json.loads(categories_data)
                    # Si c'est déjà une chaîne avec des guillemets, nettoyer
                    if isinstance(cat_value, str) and cat_value.startswith('"') and cat_value.endswith('"'):
                        cat_value = cat_value[1:-1]
                    request_data['categories'] = [cat_value]
                except json.JSONDecodeError:
                    # Si ce n'est pas un JSON valide, garder tel quel
                    if categories_data.startswith('"') and categories_data.endswith('"'):
                        categories_data = categories_data[1:-1]
                    request_data['categories'] = [categories_data]
        
        print("Données traitées:", request_data)
        
        serializer = self.get_serializer(instance, data=request_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
      
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(count=F('nombre_article')).order_by('count')
    serializer_class = CategorySerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

@api_view(['POST'])
def modifier_article(request,id):
    article= get_object_or_404(Article,id=id)

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


from django.core.cache import cache

@api_view(['POST'])
def toggle_like(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    user_ip = get_client_ip(request)

    like_key = f"like_{article_id}_{user_ip}"
    liked_before = cache.get(like_key)

    if liked_before:
        article.likes -= 1
        cache.delete(like_key)
        liked = False
    else:
        article.likes += 1
        cache.set(like_key, True, timeout=None)  
        liked = True

    article.save()

    return Response({"nombre de likes": article.likes, "liked": liked})

def get_client_ip(request):
    """Récupère l'adresse IP de l'utilisateur."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
