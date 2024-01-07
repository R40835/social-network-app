import factory

from users.models import User
from django.core.files.images import ImageFile
from io import BytesIO
from PIL import Image
from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    date_of_birth = factory.Faker("date_of_birth")

    @factory.lazy_attribute
    def profile_photo(self):
        # Generate a dummy image and save it as an ImageFieldFile
        image = Image.new("RGB", (100, 100), "white")
        image_file = BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)
        return ImageFile(image_file, name="dummy.jpg")