import cv2
import numpy as np
from tile_analyzer import detect_scorable_tiles

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

def generate_annotated_image(image_path, save_path):
    print(f"generate_annotated_image called with: {image_path} -> {save_path}")
    analysis = _analyze_tiles(image_path)
    print(f"Analysis result: {analysis}")
    # Handle error cases
    if analysis['total_tiles'] == 0 or analysis['image'] is None:
        print("Returning False - no tiles or no image")
        return False
    
    image = analysis['image'].copy()  # Work on a copy
    
    print(f"Checking {len(analysis['tiles'])} scorable tiles for objects...")
    
    for tile_data in analysis['tiles']:
        left, top, right, bottom = tile_data['boundary']
        object_type = tile_data['object_type']
        
        # Determine color and label (your existing logic)
        if object_type:
            color = (0, 0, 190)  # Red for detected objects
            
            if "buoy" in object_type:
                label = "2"
            elif object_type == "lighthouse":
                label = "3"
            elif object_type == "beacon_hq":
                label = "3"
            else:
                label = "?"
        else:
            color = (128, 0, 128)  # Purple for empty
            label = "1"
        
        # Draw rectangle and label
        cv2.rectangle(image, (int(left), int(top)), (int(right), int(bottom)), color, 3)
        cv2.putText(image, label, (int(left + 20), int(top + 45)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 5)
    
    success = cv2.imwrite(save_path, image)
    return success

def calculate_board_score(image_path):
    analysis = _analyze_tiles(image_path)
    
    # Handle error case
    if analysis['total_tiles'] == 0:
        return {
            'score': 0,
            'rank': get_rank_for_score(0),
            'breakdown': {'buoys': 0, 'lighthouses': 0, 'empty': 0}
        }
    
    # Count object types from analysis data
    buoy_count = 0
    lighthouse_count = 0
    empty_count = 0
    
    for tile_data in analysis['tiles']:
        object_type = tile_data['object_type']
        
        if object_type and "buoy" in object_type:
            buoy_count += 1
        elif object_type in ["lighthouse", "beacon_hq"]:
            lighthouse_count += 1
        else:
            empty_count += 1
    
    # Calculate score and return
    final_score = empty_count + (buoy_count * 2) + (lighthouse_count * 3)
    rank = get_rank_for_score(final_score)
    
    return {
        'score': final_score,
        'rank': rank,
        'breakdown': {
            'buoys': buoy_count,
            'lighthouses': lighthouse_count, 
            'empty': empty_count
        }
    }

def get_rank_for_score(score):
    """
    Convert a Beacon Patrol score to rank and description.
    
    Args:
        score (int): The total points scored
        
    Returns:
        tuple: (rank_name, description)
    """
    if score <= 25:
        return "Novices", "It's easy to get lost at sea. Keep trying!"
    elif score <= 35:
        return "Sailors", "Looks like you're starting to learn the ropes!"
    elif score <= 45:
        return "Captains", "A solid effort! The wind is at your back."
    elif score <= 55:
        return "Navigators", "Great job! The mysteries of these waters are second nature to you."
    else:
        return "Cartographers", "Incredible work! The good folks of the North Sea Coast will tell stories of your prowess for years to come."
    
def _analyze_tiles(image_path):
    print(f"Analyzing tiles for: {image_path}")
    
    # Check if image loads
    image = cv2.imread(image_path)
    if image is None:
        print("Could not load image with cv2.imread")
        return {'tiles': [], 'total_tiles': 0, 'scorable_count': 0, 'image': None}
    
    print(f"Image loaded successfully: {image.shape}")
    
    total_tiles, scorable_count, annotated_image, scorable_boundaries = detect_scorable_tiles(image_path)
    print(f"detect_scorable_tiles returned: total={total_tiles}, scorable={scorable_count}")
    
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
        return {
            'tiles': [],
            'total_tiles': 0,
            'scorable_count': 0,
            'image': None
        }
    
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        return {
            'tiles': [],
            'total_tiles': 0,
            'scorable_count': 0,
            'image': None
        }
        
    # The main analysis loop (from your existing functions)
    tiles_data = []
    for _i, (left, top, right, bottom) in enumerate(scorable_boundaries):
        # Extract tile region
        tile = image[int(top):int(bottom), int(left):int(right)]
        
        # Detect scored object
        object_type, confidence = detect_scored_object_in_tile(tile, template_paths)
        
        # Store the results
        tiles_data.append({
            'boundary': (left, top, right, bottom),
            'object_type': object_type,
            'confidence': confidence
        })
    
    return {
        'tiles': tiles_data,
        'total_tiles': total_tiles,
        'scorable_count': scorable_count,
        'image': image
    }

if __name__ == "__main__":
    # Quick test
    
    image_path = "test_images/valid_boards/board_18.jpg"
    total_tiles, scorable_count, annotated_image, scorable_tile_boundaries = detect_scorable_tiles(image_path)
    
    if total_tiles > 0:
        print(f"Testing scored object detection on {total_tiles} tiles...")
        # You'll need to get scorable_tile_boundaries from your tile_analyzer
        visualize_scored_objects_detection(image_path, scorable_tile_boundaries)
    else:
        print("No tiles detected to test with")