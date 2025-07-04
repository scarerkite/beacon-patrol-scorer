import cv2
import numpy as np

def detect_scored_object_in_tile(tile_image, template_paths, threshold=0.4):
    """
    Detect scored objects using blue water percentage to distinguish buoys from lighthouses
    """
    if len(tile_image.shape) == 3:
        gray_tile = cv2.cvtColor(tile_image, cv2.COLOR_BGR2GRAY)
        color_tile = tile_image.copy()
    else:
        gray_tile = tile_image
        color_tile = cv2.cvtColor(tile_image, cv2.COLOR_GRAY2BGR)
    
    best_match = None
    best_confidence = 0
    
    # Calculate blue percentage of the entire tile
    blue_percentage = calculate_blue_percentage(color_tile)
    print(f"Tile size: {gray_tile.shape}, Blue percentage: {blue_percentage:.1f}%")
    
    for template_name, template_path in template_paths.items():
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"Warning: Could not load template {template_path}")
            continue
            
        result = cv2.matchTemplate(gray_tile, template, cv2.TM_CCOEFF_NORMED)
        _, max_confidence, _, max_loc = cv2.minMaxLoc(result)

        template_h, template_w = template.shape
        print(f"  {template_name}: {max_confidence:.3f} (template size: {template.shape})")
        
        
        buoy_templates = ["buoy_birds", "buoy_birds2", "buoy_blue", "buoy_score"]
        lighthouse_templates = ["lighthouse", "beacon_hq"]

        if template_name in buoy_templates:
            if blue_percentage > 20 or max_confidence > 0.6:
                # For buoy candidates, check for red color
                x, y = max_loc
                roi = color_tile[y:y+template_h, x:x+template_w]
                
                if has_red_color(roi):
                    print(f"    -> RED DETECTED - buoy valid")
                else:
                    print(f"    -> NO RED - buoy rejected")
                    max_confidence = 0
            else:
                max_confidence = 0
                
        elif template_name in lighthouse_templates:
            if blue_percentage < 50:
                # For lighthouse candidates, also check for red color
                x, y = max_loc
                roi = color_tile[y:y+template_h, x:x+template_w]
                
                if has_red_color(roi):
                    print(f"    -> RED DETECTED - lighthouse valid")
                else:
                    print(f"    -> NO RED - lighthouse rejected")
                    max_confidence = 0
            else:
                print(f"    -> TOO MUCH WATER - lighthouse rejected")
                max_confidence = 0
        
        if max_confidence > threshold and max_confidence > best_confidence:
            best_match = template_name
            best_confidence = max_confidence
    
    print(f"  -> Best match: {best_match} ({best_confidence:.3f})")
    return best_match, best_confidence

def calculate_blue_percentage(image):
    """Calculate what percentage of the image is blue (water) - with debug output"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Try more lenient blue range
    lower_blue = np.array([90, 30, 30])   # Wider range
    upper_blue = np.array([140, 255, 255])
    
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    blue_pixels = cv2.countNonZero(blue_mask)
    total_pixels = image.shape[0] * image.shape[1]
    
    percentage = (blue_pixels / total_pixels) * 100
    
    # Debug: show what the mask looks like
    print(f"    Blue detection: {blue_pixels}/{total_pixels} pixels")
    # Uncomment to see the blue mask:
    # cv2.imshow("Blue Mask", blue_mask)
    # cv2.waitKey(1000)
    
    return percentage
def has_red_color(image_roi):
    """
    Check if the region of interest contains red color (for buoy detection)
    """
    # Convert to HSV for better red detection
    hsv = cv2.cvtColor(image_roi, cv2.COLOR_BGR2HSV)
    
    # Define red color range in HSV - let's be more lenient
    lower_red1 = np.array([0, 30, 30])    # Lower saturation/value thresholds
    upper_red1 = np.array([15, 255, 255]) # Wider hue range
    lower_red2 = np.array([165, 30, 30])  # Wider hue range
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 + mask2
    
    red_pixels = cv2.countNonZero(red_mask)
    total_pixels = image_roi.shape[0] * image_roi.shape[1]
    red_percentage = red_pixels / total_pixels
    
    print(f"    Red analysis: {red_pixels}/{total_pixels} = {red_percentage:.3f}")
    
    return red_percentage > 0.02  # Lower threshold - 2% instead of 5%

def visualize_scored_objects_detection(image_path, tile_boundaries):
    """
    Visual test function - shows scored object detection results on image
    """
    template_paths = {
        "beacon_hq": "images/templates/bp_hq_score_3.png",
        "lighthouse": "images/templates/lighthouse_score_3.png", 
        "buoy_birds": "images/templates/small_buoy_birds_score_1.png",
        "buoy_birds2": "images/templates/small_buoy_birds2_score_1.png",
        "buoy_blue": "images/templates/small_buoy_blue_score_1.png",
        "buoy_score": "images/templates/small_buoy_score_1.png"
    }
    
    total_tiles, scorable_count, annotated_image, scorable_boundaries = detect_scorable_tiles(image_path)
    
    if total_tiles == 0:
        print("No tiles detected")
        return
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"Could not load image: {image_path}")
        return
    
    print(f"Checking {len(scorable_boundaries)} scorable tiles for objects...")
    
    for _i, (left, top, right, bottom) in enumerate(scorable_boundaries):
        # Extract tile region
        tile = image[int(top):int(bottom), int(left):int(right)]
        
        # Detect scored object
        object_type, confidence = detect_scored_object_in_tile(tile, template_paths)
        
        # Draw tile boundary - different colors for different results
        # In visualize_scored_objects_detection, update the labeling section:

        if object_type:
            color = (0, 0, 139)  # Red for detected objects
            
            # Create clear, short labels
            if "buoy" in object_type:
                label = "B2"  # Buoy = 2 points
            elif object_type == "lighthouse":
                label = "L3"  # Lighthouse = 3 points  
            elif object_type == "beacon_hq":
                label = "HQ3" # Beacon HQ = 3 points
            else:
                label = "?"
        else:
            color = (139, 69, 19)  # Blue for scorable but empty
            label = "E1"  # Empty = 1 point

        cv2.rectangle(image, (int(left), int(top)), (int(right), int(bottom)), color, 3)

        # Bigger, more readable text
        cv2.putText(image, label, (int(left + 10), int(top + 30)),  # Moved inside the box
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)  # Larger font size and thickness
    
    cv2.imshow("Scorable Tiles - Object Detection", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Quick test
    from tile_analyzer import detect_scorable_tiles
    
    image_path = "test_images/valid_boards/board_18.jpg"
    total_tiles, scorable_count, annotated_image, tile_boundaries = detect_scorable_tiles(image_path)
    
    if total_tiles > 0:
        print(f"Testing scored object detection on {total_tiles} tiles...")
        # You'll need to get tile_boundaries from your tile_analyzer
        visualize_scored_objects_detection(image_path, tile_boundaries)
    else:
        print("No tiles detected to test with")