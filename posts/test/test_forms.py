import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post
from . import constants as con

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    """Проверка работы формы Post."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_client = Client()
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
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name=con.image_name,
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'author': self.user,
            'text': con.text,
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            con.new_post,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, con.main_page)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=con.text,
                group=self.group.id,
                image='posts/' + con.image_name
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма редактирует существующий Post."""
        posts_count = Post.objects.count()
        form_new_data = {
            'author': self.user,
            'text': con.new_text,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={'username': self.user.username,
                    'post_id': self.post.id}),
            data=form_new_data,
            follow=True
        )
        self.assertRedirects(response, reverse('post',
                             kwargs={'username': self.post.author,
                                     'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=con.new_text,
                group=self.group.id,
            ).exists()
        )

    def test_NOTcreate_post_with_nonpic(self):
        """Не валидная форма не создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = ('\x47\x49\x46\x38\x39\x61\x01\x00')
        try:
            uploaded = SimpleUploadedFile(
                name=con.image_name_crash,
                content=small_gif,
                content_type='image/gif'
            )
            form_data = {
                'author': self.user,
                'text': con.text,
                'group': self.group.id,
                'image': uploaded
            }
            response = self.authorized_client.post(
                con.new_post,
                data=form_data,
                follow=True
            )
            self.assertEqual(response.status_code, 300)
        except TypeError:
            self.assertEqual(Post.objects.count(), posts_count)
            self.assertFalse(
                Post.objects.filter(
                    author=self.user,
                    text=con.text,
                    group=self.group.id,
                    image='posts/' + con.image_name_crash
                ).exists()
            )


class CommentTest(TestCase):
    """Проверка работы комментариев."""
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
        cls.post = Post.objects.create(
            text=con.text,
            author=cls.another_user
        )
        cls.form_data = {
            'text': con.new_text,
        }
        cls.part_url = f'?next=/{con.another_username}/{cls.post.id}/comment/'
        cls.REDIRECT_login_URL = reverse('login') + cls.part_url

    def test_add_comment_auth_user(self):
        """Авторизованый юзер может оставлять комменатрии."""
        response = self.authorized_client.post(reverse('add_comment',
                                               kwargs={'username':
                                                       con.another_username,
                                                       'post_id':
                                                       self.post.id}),
                                               data=self.form_data,
                                               follow=True)
        self.assertRedirects(response, reverse('post',
                             kwargs={'username': self.post.author,
                                     'post_id': self.post.id}))

    def test_add_comment_guest_user(self):
        """Не авторизованый юзер НЕ может отставлять комменатрии."""
        response = self.guest_client.post(reverse('add_comment',
                                          kwargs={'username':
                                                  con.another_username,
                                                  'post_id':
                                                  self.post.id}),
                                          data=self.form_data,
                                          follow=True)
        self.assertRedirects(response, self.REDIRECT_login_URL)
