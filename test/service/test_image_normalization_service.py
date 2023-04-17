import io

from service.image_normalization_service import ImageNormalizationService, IMAGE_FORMAT
from PIL import Image


def test_normalize():
    with open("test/resources/image-jpg.jpeg", mode="rb") as f:
        res = ImageNormalizationService().normalize(f.read())

    normalized = Image.open(io.BytesIO(res))
    assert normalized.format.lower() == IMAGE_FORMAT.lower()
