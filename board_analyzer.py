from PIL import Image

def is_blue(pixel):
    r, g, b = pixel

    return b > r and b > g and b > 100

def analyze_board_colors(image_data):
    image_data.seek(0)
    img = Image.open(image_data)

    img = img.convert("RGB")
    pixels = list(img.getdata())

    sampled_pixels = pixels[::50]  # Every 50th pixel

    blue_count = 0
    for pixel in sampled_pixels:
        if is_blue(pixel):
            blue_count += 1

    blue_percentage = blue_count / len(sampled_pixels)
    print(f"Blue percentage: {blue_percentage:.2f}")

    return blue_percentage > 0.5  # 50% threshold
    

