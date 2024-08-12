def compute_layout(image_path: str):
    from PIL import Image

    image = Image.open(image_path)
    width, height = image.size
    return "portrait" if height > width else "landscape"
