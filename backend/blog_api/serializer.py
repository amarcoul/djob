from rest_framework import serializers
from .models import *
from django.conf import settings
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    articles_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = [ 'nom', 'articles_count']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nom']

class ArticleSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True) 
    auteur = UserSerializer()

    class Meta:
        model = Article
        fields = ['id', 'titre', 'contenu', 'image', 'date_publication', 'categories', 'vue', 'likes', 'auteur']

    def get_image(self, obj):
        if obj.image:
            return f"{settings.SITE_URL}{settings.MEDIA_URL}{obj.image.url}"
        return None
    
class AddArticleSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True  # Ce champ est utilisé uniquement pour l'écriture (création/mise à jour)
    )

    class Meta:
        model = Article
        fields = ['id', 'titre', 'contenu', 'image', 'categories', 'auteur']

    def create(self, validated_data):
        categories_data = validated_data.pop('categories')
        article = Article.objects.create(**validated_data)
        
        for category_name in categories_data:
            category, created = Category.objects.get_or_create(nom=category_name)
            article.categories.add(category)
        
        return article

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories')
        instance.titre = validated_data.get('titre', instance.titre)
        instance.contenu = validated_data.get('contenu', instance.contenu)
        instance.image = validated_data.get('image', instance.image)
        instance.auteur = validated_data.get('auteur', instance.auteur)
        instance.save()

        instance.categories.clear()
        for category_name in categories_data:
            category, created = Category.objects.get_or_create(nom=category_name)
            instance.categories.add(category)

        return instance