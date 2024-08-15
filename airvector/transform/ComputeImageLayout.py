def compute_layout(image_path: str):
    import PIL

    PIL.Image.MAX_IMAGE_PIXELS = 933120000

    image = PIL.Image.open(image_path)
    width, height = image.size
    return "portrait" if height > width else "landscape"
