from django.db import models

class Articles(models.Model):

    title = models.CharField(max_length= 100, verbose_name='Название медианосителя')

    def __str__(self):
        return  self.title

    class Meta:
        verbose_name='Медианоситель'
        verbose_name_plural = 'Медианосители'

class Member(models.Model):

    name=models.CharField(max_length=255,verbose_name='имя музыканта')
    slug =models.SlugField()

    def __str__(self):
        return  self.name

    class Meta:
        verbose_name='Музыкант'
        verbose_name_plural = 'Музыканты'

