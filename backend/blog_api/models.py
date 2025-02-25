from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    date_creation = models.DateTimeField(auto_now_add=True)
    photo_profil = models.ImageField(upload_to='media/users/profiles/', null=True, blank=True)  
    bio = models.TextField(null=True, blank=True) 

    def __str__(self):
        return f"{self.email}-{self.password}"

class Category(models.Model):
    nom = models.CharField(max_length=255, primary_key=True)  
    nombre_article = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nom} {self.nombre_article}"

class Article(models.Model):
    titre = models.CharField(max_length=255)
    contenu = models.TextField()
    image = models.ImageField(upload_to='media/articles/images/', null=True, blank=True)
    date_publication = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, related_name='articles')
    vue=models.PositiveIntegerField(default=0)
    likes=models.PositiveBigIntegerField(default=0)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    def __str__(self):
        return self.titre
    
class Tag(models.Model):
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')  # Empêche un utilisateur de liker plusieurs fois

    def __str__(self):
        return f"{self.user.email} - {self.article.titre}"
