from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

from . import constants as con

User = get_user_model()
urls = [con.main_page,
        con.group_page,
        con.new_post,
        con.user_page]


class PostURLTests(TestCase):
    """Проверка URL адресов."""
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
        cls.group = Group.objects.create(
            title=con.group_name,
            slug=con.group_slug,
            description=con.description
        )
        cls.post = Post.objects.create(
            text=con.text,
            author=cls.user,
            group=cls.group
        )
        cls.urls = urls
        cls.urls.append(f'/{con.username}/{cls.post.id}/')
        cls.urls.append(f'/{con.username}/{cls.post.id}/edit/')
        cls.urls.append(f'/{con.username}/{cls.post.id}/delete/')

        cls.anonimus_url_code = [200, 200, 302, 200, 200, 302, 302]
        cls.user_url_code = [200, 200, 200, 200, 200, 302, 302]
        cls.user_author_url_code = [200, 200, 200, 200, 200, 403, 403]

    def test_url_guest_user(self):
        """Проверка дотсупа к страницам не авторизованых пользователей."""
        url_and_status_code = dict(zip(self.urls, self.anonimus_url_code))
        for url_name, status_code in url_and_status_code.items():
            with self.subTest():
                response = self.guest_client.get(url_name)
                self.assertEqual(response.status_code, status_code)

    def test_url_authorized_user(self):
        """Проверка дотсупа к страницам авторизованых пользователей."""
        url_and_status_code = dict(zip(self.urls, self.user_url_code))
        for url_name, status_code in url_and_status_code.items():
            with self.subTest():
                response = self.authorized_client.get(url_name)
                self.assertEqual(response.status_code, status_code)

    def test_url_authorized_user(self):
        """Проверка дотсупа к страницам пользователей другого пользователя."""
        url_and_status_code = dict(zip(self.urls, self.user_author_url_code))
        for url_name, status_code in url_and_status_code.items():
            with self.subTest():
                response = self.authorized_another_client.get(url_name)
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_names = [
            'index.html',
            'group.html',
            'new_post.html',
            'profile.html',
            'post.html',
            'new_post.html',
        ]
        templates_and_urls_names = dict(zip(self.urls, template_names))
        for url_name, template_name in templates_and_urls_names.items():
            with self.subTest():
                response = self.authorized_client.get(url_name)
                self.assertTemplateUsed(response, template_name)

    def test_url_guest_user(self):
        """Проверка получения кода 404 при несуществующей старнице."""
        with self.subTest():
            response = self.guest_client.get(con.none_page)
            self.assertEqual(response.status_code, 404)
