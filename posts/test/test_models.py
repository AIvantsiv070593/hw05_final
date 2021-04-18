from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post
from . import constants as con

User = get_user_model()


class PostModelTest(TestCase):
    """Тест модели Post и Group"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=con.username)
        cls.group = Group.objects.create(
            title=con.group_name,
            slug=con.group_slug,
            description=con.description
        )
        cls.post = Post.objects.create(
            text=con.text * 10,
            author=cls.user,
            group=cls.group
        )

    def test_verbose_name(self):
        """Проверка человекочетаемого имени атрибута."""
        field_verboses = {
            'text': con.text_model,
            'group': con.group_model
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """Проверка текста подсказки."""
        field_help_texts = {
            'text': con.help_text,
            'group': con.help_group
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text, expected)

    def test_len_post_text(self):
        """Проверка длины вовода текста поста."""
        expected_text = self.post.text[:15]
        self.assertEquals(expected_text, str(self.post))

    def test_gorup_name(self):
        """Проверка имени группы поста."""
        expected_group_name = self.group.title
        self.assertEquals(expected_group_name, con.group_name)
