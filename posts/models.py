from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Группировка постов по темам с описанием."""
    title = models.CharField('NameGroup', max_length=200, default='TestGroup')
    slug = models.SlugField('uniqueSlug', unique=True, default='')
    description = models.TextField('Description')

    class Meta:
        verbose_name = 'GroupPost'

    def __str__(self):
        return f'{self.title}'


class Post(models.Model):
    """Посты авторов."""
    text = models.TextField(verbose_name='Текст',
                            help_text='Напишите что нибудь')
    pub_date = models.DateTimeField('date published',
                                    auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, models.SET_NULL,
                              blank=True,
                              null=True,
                              verbose_name='Группа',
                              help_text='Выберите группу')
    image = models.ImageField(upload_to='posts/',
                              blank=True,
                              null=True,
                              help_text='Добавте картинку')

    class Meta:
        verbose_name = 'AuthorPost'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.text[:15]}'


class Comment(models.Model):
    """Комменатрии к постам"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField(verbose_name='Комментарий',
                            help_text='Оставь комментарий')
    created = models.DateTimeField('date created',
                                   auto_now_add=True,
                                   db_index=True)

    class Meta:
        verbose_name = 'CommentPost'
        ordering = ('-created',)

    def __str__(self):
        return f'{self.text[:10]}'


class Follow(models.Model):
    """Подписка на пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')

    def __str__(self):
        return f'Подписок {self.user.count()},'
        f'Подписавшихся {self.author.count()}'
