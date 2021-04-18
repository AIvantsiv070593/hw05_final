from django.urls import reverse

# Post
username = 'UserTest'
another_username = 'AnotherUserTest'
text = 'TestText'
new_text = 'NewTestText'
image_name = 'testImage.png'

# for Group
group_name = 'TestGroup'
group_slug = 'TestSlug'
description = 'DiscriptionTest'

# urls
main_page = reverse('index')
new_post = reverse('new_post')
group_page = reverse('group', kwargs={'slug': group_slug})
user_page = reverse('profile', kwargs={'username': username})
user_another_page = reverse('profile', kwargs={'username': another_username})
none_page = '/nonpage/'

# for model field_verboses
text_model = 'Текст'
group_model = 'Группа'


# fro model field_help_texts
help_text = 'Напишите что нибудь'
help_group = 'Выберите группу'
