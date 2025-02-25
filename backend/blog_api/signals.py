
from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver
from .models import Article, Category

@receiver(m2m_changed, sender=Article.categories.through)
def mise_a_jour_nombre_article_apres_ajout(sender, instance, action, **kwargs):

    if action in ["post_add", "post_remove", "post_clear"]:
        for category in instance.categories.all():
            category.nombre_article = category.articles.count()  # Met à jour le nombre d'articles
            category.save()

@receiver(post_delete, sender=Article)
def mise_a_jour_nombre_article_apres_suppression(sender, instance, **kwargs):

    for category in instance.categories.all():
        category.nombre_article = category.articles.count()  # Recalcul du nombre d'articles
        category.save()