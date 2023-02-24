from django.test import TestCase
from django.contrib.auth.models import User
from webserver.models import Profile


# Create your tests here.
class ProfileModelTests(TestCase):
    def test_user_name(self):
        user = User.objects.create_user(username="annyshi", first_name="Anny", last_name="Shi")
        profile = Profile(user=user)
        self.assertEqual("annyshi", profile.user.username)
        self.assertEqual("Anny", profile.user.first_name)
        self.assertEqual("Shi", profile.user.last_name)
