import io

from PIL import Image

IMAGE_FORMAT = "png"


class ImageNormalizationService:
    def normalize(self, image_data: bytes) -> bytes:
        image = Image.open(io.BytesIO(image_data))

        # Convert the image to PNG format
        image_png = io.BytesIO()
        image.save(image_png, format=IMAGE_FORMAT)
        image_png.seek(0)
        return image_png.getvalue()

    def normalize_file_name(self, file_name: str):
        if file_name.endswith(".png"):
            return file_name

        file_name = file_name[:file_name.rfind(".")]
        return f"{file_name}.png"
