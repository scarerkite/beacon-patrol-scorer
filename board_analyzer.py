from PIL import Image
import cv2
import numpy as np
from arrow_detection import validate_board_arrows 

def is_blue(pixel):
    r, g, b = pixel

    return b > r and b > g and b > 100

def analyze_board_colors(image_data):
    # If it's BytesIO, convert to PIL Image
    if hasattr(image_data, 'read'):
        image_data.seek(0)
        img = Image.open(image_data)
    else:
        # It's already a PIL Image
        img = image_data

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

def analyze_full_board(image_path):
    return validate_board_arrows(image_path)

# if __name__ == "__main__":
#     is_valid, message, correct_count, incorrect_count, annotated_image = analyze_full_board("test_images/invalid_boards/5_tiles_3_arrows_wrong.jpg")
#     print(f"Result: {is_valid}")
#     print(f"Message: {message}")
#     print(f"Correct count: {correct_count}")
#     print(f"Incorrect count: {incorrect_count}")

#     cv2.imshow("Debug Arrow Detection", annotated_image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
