from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()

urls = ['/about/author/',
        '/about/tech/']


class PostURLTests(TestCase):
    """Проверка URL адресов."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.urls = [
            '/about/author/',
            '/about/tech/'
        ]
        cls.template_names = [
            'about/author.html',
            'about/tech.html',
        ]

    def test_url_statik_page_guest_user(self):
        """Проверка дотсупа к страницам не авторизованых пользователей."""
        for url_name in urls:
            with self.subTest():
                response = self.guest_client.get(url_name)
                self.assertEqual(response.status_code, 200)

    def test_urls_statik_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_and_template_page = dict(zip(urls, self.template_names))
        for url_name, template_name in url_and_template_page.items():
            with self.subTest():
                response = self.guest_client.get(url_name)
                self.assertTemplateUsed(response, template_name)
