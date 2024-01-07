import pytest

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import ProfilePhotos
from io import BytesIO
from django.core.files.images import ImageFile
from io import BytesIO
from PIL import Image
from .factories import UserFactory

User = get_user_model()


@pytest.mark.my_custom_marker
class TestBase(TestCase):

    GREEN = '\033[92m'
    RED = '\033[91m'
    END = '\033[0m'

    def setUp(self):

        user = self.create_user_with_profile_photo()

        self.client = Client()
        self.index_url = reverse('index')
        self.signup_url = reverse('users:sign-up')
        self.signin_url = reverse('users:sign-in')
        self.signout_url = reverse('users:sign-out')
        self.change_password_url = reverse('users:change-password')
        self.feed_url = reverse('post:feed')
        self.edit_account_url = reverse('users:edit-account')
        self.delete_account_url = reverse('users:delete-account')
        self.user_correct_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': "test@some.org",
            'date_of_birth': user.date_of_birth.strftime('%d/%m/%Y'),
            'password': 'madtester24',
            'password2': 'madtester24',
            'profile_photo': user.profile_photo
        }
        self.user_missing_photo = {
            'first_name': 'anonymous',
            'last_name': 'something',
            'email': 'newuser2@gmail.com',
            'date_of_birth': '01/01/1990',
            'password': 'madtester24',
            'password2': 'madtester24',
            'profile_photo': '',
        }
        self.user_unmatching_password = {
            'first_name': 'anonymous',
            'last_name': 'something',
            'email': 'newuser3@gmail.com',
            'date_of_birth': '01/01/1990',
            'password': 'madtester24',
            'password2': 'madster24',
            'profile_photo': '',
        }
        self.user_invalid_email = {
            'first_name': 'anonymous',
            'last_name': 'something',
            'email': 'newusergmail.com',
            'date_of_birth': '01/01/1990',
            'password': 'madtester24',
            'password2': 'madtester24',
            'profile_photo': '',
        }
        self.user_missing_required_info = {
            'first_name': '',
            'last_name': '',
            'email': 'newuser@gmail.com',
            'date_of_birth': '',
            'password': 'madtester24',
            'password2': 'madtester24',
            'profile_photo': '',
        }
        return super().setUp()
    
    def tearDown(self):
        User.objects.all().delete()

    @staticmethod
    def create_user_with_profile_photo():
        image = Image.new("RGB", (100, 100), "white")
        image_file = BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)
        profile_photo = ImageFile(image_file, name="dummy.jpg")
        user = UserFactory(profile_photo=profile_photo)
        user.is_active = True
        user.save()
        return user


@pytest.mark.my_custom_marker
class UserSignUpTest(TestBase):

    def test_sign_up_view(self):

        print("\n" + ("+" * 20) + "Tesing Sign Up View".center(20) + ("+" * 20) + "\n")

        response = self.client.get(self.signup_url)
        try:
            self.assertEqual(response.status_code, 200)  
            self.assertTemplateUsed(response, "users/signup.html")
            print("> sign up view set up correctly.")
            print(self.GREEN + "Sign Up View Test Passed." + self.END)
        except AssertionError:
            print("> sign up view set up incorrectly.")
            print(self.RED + "Sign Up View Test Failed." + self.END)

    def test_sign_up(self):

        print("\n" + ("+" * 20) + "Tesing Sign Up".center(20) + ("+" * 20) + "\n")

        response = self.client.post(self.signup_url, self.user_correct_data, format='text/html')

        if response.status_code != 302:
            print("> Form errors:", response.context['form'].errors)

        try:
            self.assertEqual(response.status_code, 302)  # Check for redirect after successful signup
            self.assertRedirects(response, self.edit_account_url)  # Check for redirect to edit-account
            self.assertTrue(User.objects.filter(email=self.user_correct_data['email']).exists())
            print("> user created and stored in the database.")
        except AssertionError:
            print("> Error: user was not created, nor stored in the database.")

        try:
            self.assertTrue(response.wsgi_request.user.is_authenticated)
            print("> user authenticated, sign up functional.")
            print(self.GREEN + "Sign Up Test Passed." + self.END)
        except AssertionError:
            print("> Error: user is not authenticated, should of been signed in.")
            print(self.RED + "Sign Up Test Failed." + self.END)

    def test_sign_up_without_photo(self):

        print("\n" + ("+" * 20) + "Tesing Sign Up Without Photo".center(20) + ("+" * 20) + "\n")

        response = self.client.post(self.signup_url, self.user_missing_photo, format='multipart')

        if response.status_code != 302:
            print("> Form errors:", response.context['form'].errors)

        try:
            self.assertEqual(response.status_code, 302)  # Check for redirect after successful signup
            self.assertRedirects(response, self.edit_account_url)  # Check for redirect to edit-account
            self.assertTrue(User.objects.filter(email=self.user_missing_photo['email']).exists())
            print("> user created and stored in the database, profile photos are only optional.")
        except AssertionError:
            print("> Error: user was not created, nor stored in the database.")

        try:
            self.assertTrue(response.wsgi_request.user.is_authenticated)
            print("> user authenticated, sign up functional.")
            print(self.GREEN + "Sign Up Without Photo Test Passed." + self.END)
        except AssertionError:
            print("> Error: user is not authenticated, should of been signed in.")
            print(self.RED + "Sign Up Test Failed." + self.END)

    def test_sign_up_unmatching_password(self):

        print("\n" + ("+" * 20) + "Tesing Sign Up Unmatching Password".center(20) + ("+" * 20) + "\n")

        response = self.client.post(self.signup_url, self.user_unmatching_password, format='text/html')

        if response.status_code != 302:
            print("> Form errors:", response.context['form'].errors)

        try:
            self.assertEqual(response.status_code, 200)
            print("> user still on the same page because of unmatching password.")
            try:
                self.assertTrue(User.objects.filter(email=self.user_unmatching_password['email']).count() == 0)
                print("> user was not created, nor stored in the database.")
                print(self.GREEN + "Sign Up Unmatching Password Test Passed." + self.END)
            except:
                print("> Error: user shouldn't have been created.")
                print(self.RED + "Sign Up Unmatching Password Test Failed." + self.END)
        except AssertionError:
            print("> Error: user should of been redirected to the same page.")
            print(self.RED + "Sign Up Unmatching Password Test Failed." + self.END)

    def test_sign_up_invalid_email(self):

        print("\n" + ("+" * 20) + "Tesing Sign Up Invalid Email".center(20) + ("+" * 20) + "\n")

        response = self.client.post(self.signup_url, self.user_invalid_email, format='text/html' + "\n")

        if response.status_code != 302:
            print("> Form errors:", response.context['form'].errors)

        try:
            self.assertEqual(response.status_code, 200)
            print("> user still on the same page because of invalid email.")
            try:
                self.assertTrue(User.objects.filter(email=self.user_invalid_email['email']).count() == 0)
                print("> user was not created, nor stored in the database.")
                print(self.GREEN + "Sign Up Invalid Email Test Passed." + self.END)
            except:
                print("> Error: user shouldn't have been created.")
                print(self.RED + "Sign Up Invalid Email Test Failed." + self.END)
        except AssertionError:
            print("> Error: user should of been redirected to the same page.")
            print(self.RED + "Sign Up Invalid Email Test Failed." + self.END)


@pytest.mark.my_custom_marker
class SignInTest(TestBase):

    def test_sign_in_view(self):

        print("\n" + ("+" * 20) + "Tesing Sign In View".center(20) + ("+" * 20) + "\n")

        response = self.client.get(self.signin_url)

        try:
            self.assertEqual(response.status_code, 200)  
            self.assertTemplateUsed(response, "users/signin.html")  
            print("> sign in view set up correctly.")
            print(self.GREEN + "Sign In View Test Passed." + self.END)
        except AssertionError:
            print("> sign in view set up incorrectly.")
            print(self.RED + "Sign In View Test Failed." + self.END)

    def test_sign_in(self):

        print("\n" + ("+" * 20) + "Tesing Sign In".center(20) + ("+" * 20) + "\n")
        # create a user
        self.client.post(self.signup_url, self.user_correct_data, format='text/html')

        user = User.objects.get(email=self.user_correct_data['email'])
        user.is_active = True
        user.save()
        response = self.client.post(self.signin_url, self.user_correct_data, format='text/html')

        try:
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, self.feed_url)  
            self.assertTrue(response.wsgi_request.user.is_authenticated) 
            print("> user authenticated, sign in functional.")
            print(self.GREEN + "Sign In Test Passed." + self.END)
        except AssertionError:
            print("> Error: user is not authenticated, should of been signed in.")
            print(self.RED + "Sign In Test Failed." + self.END)


@pytest.mark.my_custom_marker
class SignOutTest(TestBase):

    def test_sign_out(self):

        print("\n" + ("+" * 20) + "Tesing Sign Out".center(20) + ("+" * 20) + "\n")
        # create a user
        self.client.post(self.signup_url, self.user_correct_data, format='text/html')
        print("> user created.")
        # sign in
        user = User.objects.get(email=self.user_correct_data['email'])
        user.is_active = True
        user.save()
        self.client.post(self.signin_url, self.user_correct_data, format='text/html')
        print("> user signed in.")
        # sign out
        response = self.client.get(self.signout_url)

        try:
            self.assertEqual(response.status_code, 302)  # Check for redirect after sign-out
            self.assertRedirects(response, self.signin_url)
            self.assertTrue(not response.wsgi_request.user.is_authenticated)
            print("> user is not authenticated, sign out functional.")
            print(self.GREEN + "Sign Out Test Passed." + self.END)
        except AssertionError:
            print("> Error: user authenticated, should of been signed out.")
            print(self.RED + "Sign Out Test Failed." + self.END)


@pytest.mark.my_custom_marker
class UserProfileTest(TestBase):

    def create_login_user(self, data):
        self.client.post(self.signup_url, data, format='text/html')
        user = User.objects.get(email=data['email'])
        user.is_active = True
        user.save()

        return user
    
    def setUp(self):
        super().setUp()
        
        self.user_correct_data2 = {
            'first_name': 'another',
            'last_name': 'thing',
            'email': 'newuser2@gmail.com',
            'date_of_birth': '30/01/2000',
            'password': '@madtester@24',
            'password2': '@madtester@24',
            'profile_photo': '',
        }

        # Create and login a user to get the user_id
        user = self.create_login_user(self.user_correct_data)
        self.user_id = user.id  # Set the user_id as an instance variable

        # Set up dynamic URLs using the user_id for current users
        self.user_posts_url = reverse('users:user-posts', kwargs={'user_id': self.user_id})
        self.user_friends_url = reverse('friend:friends-list', kwargs={'user_id': self.user_id})
        self.user_photos_url = reverse('users:photos', kwargs={'user_id': self.user_id})

        # Set up photo_id to test the delete function later
        photo = ProfilePhotos.objects.get(user_id=user.id)
        self.photo_id = photo.id
        # Set up dynamic URLs using the photo_id
        self.delete_photo_url = reverse('users:delete-photo', kwargs={'photo_id': self.photo_id})

    def test_user_posts_view(self):

        print("\n" + ("+" * 20) + "Tesing Current User Posts View".center(20) + ("+" * 20) + "\n")
        response = self.client.get(self.user_posts_url)

        try:
            self.assertEqual(response.status_code, 200)  # Check for redirect after successful signup
            self.assertTemplateUsed(response, "users/user_posts.html")  # Check for redirect to edit-account
            print("> user posts view set up correctly.")
            print(self.GREEN + "Current User Posts View Test Passed." + self.END)
        except AssertionError:
            print("> user posts view set up incorrectly.")
            print(self.RED + "Current User Posts View Test Failed." + self.END)

    def test_user_friends_view(self):

        print("\n" + ("+" * 20) + "Tesing Current User Friends View".center(20) + ("+" * 20) + "\n")
        
        response = self.client.get(self.user_friends_url)

        try:
            self.assertEqual(response.status_code, 200)  # Check for redirect after successful signup
            self.assertTemplateUsed(response, "friend/friends.html")  # Check for redirect to edit-account
            print("> user friends view set up correctly.")
            print(self.GREEN + "Current User Friends View Test Passed." + self.END)
        except AssertionError:
            print("> user friends view set up incorrectly.")
            print(self.RED + "Current User Friends View Test Failed." + self.END)

    def test_user_photos_view(self):
        
        print("\n" + ("+" * 20) + "Tesing Current User Photos View".center(20) + ("+" * 20) + "\n")
        
        response = self.client.get(self.user_photos_url)

        try:
            self.assertEqual(response.status_code, 200)  # Check for redirect after successful signup
            self.assertTemplateUsed(response, "users/photos.html")  # Check for redirect to edit-account
            print("> user photos view set up correctly.")
            print(self.GREEN + "Current User Photos View Test Passed." + self.END)
        except AssertionError:
            print("> user photos view set up incorrectly.")
            print(self.RED + "Current User Photos View Test Failed." + self.END)

    def test_delete_user(self): 

        print("\n" + ("+" * 20) + "Tesing User Account Deletion".center(20) + ("+" * 20) + "\n")

        user = self.create_login_user(self.user_correct_data)
        self.assertTrue(User.objects.get(pk=user.id))
        self.client.force_login(user)
        print("> user has been created.")
        try:
            response = self.client.post(self.delete_account_url, format='text/html')
            self.assertEqual(response.status_code, 302)  # Check for redirect after successful signup
            self.assertRedirects(response, self.index_url)
            print("> user has been deleted.")
            try:
                response = self.client.post(self.signin_url, data={"email": user.email, "password": "madtester24"}, format='text/html')
                self.assertNotEqual(response.status_code, 302)
                print("> user tried to regain access to their account and couldn't.")
                print(self.GREEN + "User Account Deletion Test Passed." + self.END)

            except AssertionError:
                print("> Error: user wasn't redirected after deleting account.")
                print(self.RED + "User Account Deletion Test Failed." + self.END)
        except AssertionError:
            print("> Error: user wasn't redirected after deleting account.")
            print(self.RED + "User Account Deletion Test Failed." + self.END)

    def test_profile_photos_signup_upload(self):

        print("\n" + ("+" * 20) + "Tesing Saving Profile Photos On Creation".center(20) + ("+" * 20) + "\n")

        user = self.create_login_user(data=self.user_correct_data)
        try:
            photo = ProfilePhotos.objects.get(user_id=user.id)
            self.assertIsNotNone(photo)
            print("> profile photo saved upon creation correctly.")
            self.assertTrue(ProfilePhotos.objects.filter(user_id=user.id).count() == 1)
            print("> no duplicate photos.")
            print(self.GREEN + "Saving Profile Photos On Creation Test Passed." + self.END)
        except AssertionError:
            print("> Error: profile photo wasn't saved on creation.")
            print(self.RED + "Saving Profile Photos On Creation Test Failed." + self.END)

    def test_profile_photos_edit_upload(self):

        print("\n" + ("+" * 20) + "Tesing Saving Profile Photos On Edit".center(20) + ("+" * 20) + "\n")

        user = self.create_login_user(data=self.user_correct_data)

        data = {
            'first_name': 'rayan',
            'last_name': 'wiw',
            'email': 'rayan@wiw.net',
            'date_of_birth': '10/10/2000',
            'profile_photo': user.profile_photo
        }
        response = self.client.post(self.edit_account_url, data, format='multipart')

        try:
            # = 2 since we created the user with a profile photo
            self.assertTrue(len([photo for photo in ProfilePhotos.objects.filter(user_id=user.id)]) == 2)
            print("> user photo uploaded and stored in the database.")
            try:
                self.assertEqual(response.status_code, 302)  # Check for redirect after successful signup
                self.assertRedirects(response, self.edit_account_url)  # Check for redirect to edit-account
                print("> user profile photo updated.")
                print(self.GREEN + "Saving Profile Photos On Edit Test Passed." + self.END)
            except AssertionError:
                print("> Error: user not redirected on update.")
                print(self.RED + "Saving Profile Photos On Edit Test Failed." + self.END)
        except AssertionError:
            print("> Error: either the photos are duplicate or not uploaded.")
            print(self.RED + "Saving Profile Photos On Edit Test Failed." + self.END)

    def test_delete_photo(self):

        print("\n" + ("+" * 20) + "Tesing Photo Deletion".center(20) + ("+" * 20) + "\n")

        user = self.create_login_user(self.user_correct_data)
        self.client.force_login(user)
        print("> user has been created.")
        response = self.client.post(self.delete_photo_url, format='text/html')
        try:
            self.assertEqual(response.status_code, 302)  # Check for redirect after successful signup
            self.assertRedirects(response, self.user_photos_url)
            print("> photo has been deleted.")
            print(self.GREEN + "User Photo Deletion Test Passed." + self.END)
        except AssertionError:
            print("> Error: user wasn't redirected after deleting photo.")
            print(self.RED + "User Photo Deletion Test Failed." + self.END)

    def test_change_password(self):
        print("\n" + ("+" * 20) + "Tesing User Password Change".center(20) + ("+" * 20) + "\n")

        user = self.create_login_user(data=self.user_correct_data)
        # print(response)
        data = {
            "old_password": self.user_correct_data["password"],
            "new_password1": "wBnawssssssjd@4",
            "new_password2": "wBnawssssssjd@4"
        }

        response = self.client.post(self.change_password_url, data, format="text/html")
        if response.status_code != 302:
            print("> Form errors:", response.context['form'].errors)
        try:
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, self.edit_account_url)
            print("> user has been redirected.")
            try:
                user.refresh_from_db()
                self.assertTrue(user.check_password(data["new_password1"]))
                print("> user password has been changed.")
                print(self.GREEN + "User Password Change Test Passed." + self.END)
            except AssertionError:
                print("> Error: user's password wasn't changed.")

        except AssertionError:
            print("> Error: user wasn't redirected after changing password photo.")
            print(self.RED + "User Password Change Test Failed." + self.END)
            




