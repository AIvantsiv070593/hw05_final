import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from yatube.settings import paginator_count
from posts.models import Group, Post
from . import constants as con

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
templates_page_names = {con.main_page: 'index.html',
                        con.group_page: 'group.html',
                        con.new_post: 'new_post.html',
                        con.user_page: 'profile.html'}

small_gif = (b'\x47\x49\x46\x38\x39\x61\x01\x00'
             b'\x01\x00\x00\x00\x00\x21\xf9\x04'
             b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
             b'\x00\x00\x01\x00\x01\x00\x00\x02'
             b'\x02\x4c\x01\x00\x3b')
uploaded = SimpleUploadedFile(name=con.image_name,
                              content=small_gif,
                              content_type='image/gif')
image_path = 'posts/testImage.png'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    """Проверка шаблонов страниц."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=con.username)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title=con.group_name,
            slug=con.group_slug,
            description=con.description
        )
        cls.post = Post.objects.create(
            text=con.text,
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.post_count = Post.objects.filter(author=cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_tempalate_name(self):
        """Шаблоны доступны по 'name'."""
        post_page = reverse('post', kwargs={
                            'username': self.user.username,
                            'post_id': self.post.id})
        post_edit = reverse('post_edit', kwargs={
                            'username': self.user.username,
                            'post_id': self.post.id})
        templates_page_names[post_page] = 'post.html'
        templates_page_names[post_edit] = 'new_post.html'
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(con.main_page)
        for post in response.context['page']:
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.user)
            self.assertEqual(post.image, image_path)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(con.group_page)
        for post in response.context['page']:
            self.assertEqual(post.group.title, self.group.title)
            self.assertEqual(post.group.slug, self.group.slug)
            self.assertEqual(post.group.description, self.group.description)
            self.assertEqual(post.image, image_path)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(con.new_post)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(con.user_page)
        self.assertEqual(response.context['username'], self.user)
        self.assertEqual(response.context['posts_count'],
                         self.post_count.count())
        for post in response.context['page']:
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.image, image_path)

    def test_post_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('post',
                                              kwargs={'username':
                                                      self.user.username,
                                                      'post_id':
                                                      self.post.id}))
        self.assertEqual(response.context['username'], self.user)
        self.assertEqual(response.context['posts_count'],
                         self.post_count.count())
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['post'].image, image_path)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон редактирования поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('post_edit',
                                              kwargs={'username':
                                                      self.user.username,
                                                      'post_id':
                                                      self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_group_add_correct(self):
        """Пост добавлен с указанием группы."""
        response = self.authorized_client.get(con.main_page)
        for post in response.context['page']:
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.user)
            self.assertEqual(post.group, self.group)

    def test_post_group_page_show_correct(self):
        """Пост существует на странице группы."""
        response = self.authorized_client.get(con.group_page)
        for post in response.context['page']:
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.user)
            self.assertEqual(post.group, self.group)

    def test_404_page_show_correct(self):
        """Получаем ошибку 404 с правильным контекстом."""
        template = 'misc/404.html'
        response = self.authorized_client.get(con.none_page)
        self.assertTemplateUsed(response, template)


class PaginatorViewsTest(TestCase):
    """Проверка отображения Пагинатора."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=con.username)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.posts = [Post(text=con.text + str(i), author=cls.user)
                     for i in range(0, 13)]
        Post.objects.bulk_create(cls.posts)
        cls.post = Paginator(Post.objects.all(), paginator_count)

    def test_first_page_containse_ten_records(self):
        """Проверка количества постов основной старинцы."""
        response = self.authorized_client.get(con.main_page)
        self.assertEqual(len(response.context.get('page').object_list),
                         paginator_count)

    def test_second_page_containse_three_records(self):
        """Проверка количества постов на второй странице."""
        response = self.authorized_client.get(con.main_page + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)


class CacheTest(TestCase):
    """Проверка кеширования страниц."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=con.username)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title=con.group_name,
            slug=con.group_slug,
            description=con.description
        )
        cls.post = Post.objects.create(
            text=con.text,
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

    def test_cahe_index_page(self):
        """Страница index кешируется."""
        response = self.authorized_client.get(con.main_page)
        self.post = Post.objects.create(
            text=con.new_text,
            author=self.user,
            group=self.group,
            image=uploaded
        )
        response_cache = self.authorized_client.get(con.main_page)
        self.assertEqual(response.content, response_cache.content)
        cache.clear()
        response_cache_clear = self.authorized_client.get(con.main_page)
        self.assertNotEqual(response_cache_clear.content,
                            response_cache.content)


class FollowTest(TestCase):
    """Проверка работы подписки и отписки пользоватлей."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=con.username)
        cls.another_user = User.objects.create_user(
            username=con.another_username)
        cls.authorized_client = Client()
        cls.authorized_another_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_another_client.force_login(cls.another_user)
        cls.urls_name = ['index', 'follow_index']

    def test_authorization_user_follow(self):
        """Подписка на пользователя."""
        following_count = self.another_user.following.count()
        response = self.authorized_client.get(reverse('profile_follow',
                                              kwargs={'username':
                                                      con.another_username}))
        self.assertRedirects(response, con.user_another_page)
        following_count_new = self.another_user.following.count()
        self.assertEqual(following_count_new, following_count + 1)

    def test_authorization_user_unfollow(self):
        """Отписка от пользователя."""
        response = self.authorized_client.get(reverse('profile_follow',
                                              kwargs={'username':
                                                      con.another_username}))
        following_count = self.another_user.following.count()
        response = self.authorized_client.get(reverse('profile_unfollow',
                                              kwargs={'username':
                                                      con.another_username}))
        self.assertRedirects(response, con.user_another_page)
        following_count_new = self.another_user.following.count()
        self.assertEqual(following_count_new, following_count - 1)

    def test_show_follow_another_user_post(self):
        """При создание поста пост появляется в избраном у подписавшихся."""
        self.authorized_client.get(reverse('profile_follow',
                                   kwargs={'username':
                                           con.another_username}))

        self.authorized_another_client.post(
            con.new_post,
            {'text': con.text},
            follow=True)

        for name in self.urls_name:
            response = self.authorized_client.get(reverse(name))
            for post in response.context['page']:
                self.assertEqual(post.text, con.text)
                self.assertEqual(post.author, self.another_user)

    def test_show_NOT_follow_another_user_post(self):
        """При создание поста пост НЕ появляется в избраном у остальных."""
        self.authorized_another_client.post(
            con.new_post,
            {'text': con.text},
            follow=True)
        response = self.authorized_client.get(reverse('follow_index'))
        self.assertFalse(response.context.get('page').object_list.exists())
