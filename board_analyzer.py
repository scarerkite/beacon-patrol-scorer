from PIL import Image
import cv2
import numpy as np

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

def identify_blue_tiles(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    lower_blue = np.array([95, 100, 150])
    upper_blue = np.array([115, 255, 255])

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Morphological opening to separate touching blue regions
    # Temporarily takes away pixels to remove noise and find edges
    # Grows them again so the final result is roughly the right size
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 8)

    return list(contours)

    # cv2.imshow("Blue Tiles", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
# if __name__ == "__main__":
#     identify_blue_tiles()