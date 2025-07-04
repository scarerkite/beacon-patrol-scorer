from PIL import Image
import cv2
import numpy as np

def get_arrow_positions(image_path, correct_threshold=0.79, incorrect_threshold=0.79):
    """
    Detect correct and incorrect arrow orientations on a Beacon Patrol board.

    Returns:
        array of tuples
    """

    image = cv2.imread(image_path)
    if image is None:
        return [], [], None
        
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Template paths
    correct_template_path = "images/templates/arrow_tight_crop.png"

    incorrect_template_paths = [
        "images/templates/arrow_tight_90.png",
        "images/templates/arrow_tight_180.png",
        "images/templates/arrow_tight_270.png",
    ]

    correct_detections = []
    incorrect_detections = []
    
    # Find correct arrows
    template = cv2.imread(correct_template_path, cv2.IMREAD_GRAYSCALE)
    if template is not None:
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= correct_threshold)
        points = list(zip(*locations[::-1]))
        correct_detections.extend(points)
    
    # Remove duplicates from correct detections
    unique_correct_positions = []
    for point in correct_detections:
        is_duplicate = False
        for existing in unique_correct_positions:
            distance = ((point[0] - existing[0])**2 + (point[1] - existing[1])**2)**0.5
            if distance < 40:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_correct_positions.append(point)

    # Find incorrect arrows
    for template_path in incorrect_template_paths:
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            continue
            
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= incorrect_threshold)
        points = list(zip(*locations[::-1]))
        incorrect_detections.extend(points)
    
    # Remove duplicates from incorrect detections
    unique_incorrect_positions = []
    for point in incorrect_detections:
        is_duplicate = False
        for existing in unique_incorrect_positions:
            distance = ((point[0] - existing[0])**2 + (point[1] - existing[1])**2)**0.5
            if distance < 40:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_incorrect_positions.append(point)

    return unique_correct_positions, unique_incorrect_positions, image

def detect_arrow_orientations(image_path, correct_threshold=0.79, incorrect_threshold=0.79):
    """
    Two-pass arrow detection:
    1. Find correct arrows with lower threshold
    2. Find incorrect arrows, but exclude areas near correct arrows
    
    Args:
        image_path (str): Path to the board image
    
    Returns:
        tuple: (correct_count, incorrect_count, annotated_image)
    """
    image = cv2.imread(image_path)
    if image is None:
        return 0, 0, None
        
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Template paths
    correct_template_path = "images/templates/arrow_tight_crop.png"
    incorrect_template_paths = [
        "images/templates/arrow_tight_90.png",
        "images/templates/arrow_tight_180.png",
        "images/templates/arrow_tight_270.png",
    ]
    
    result_image = image.copy()
    
    # PASS 1: Find correct arrows (more lenient threshold)
    print(f"PASS 1: Looking for correct arrows (threshold: {correct_threshold})")
    correct_detections = []
    
    template = cv2.imread(correct_template_path, cv2.IMREAD_GRAYSCALE)
    if template is not None:
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= correct_threshold)
        points = list(zip(*locations[::-1]))
        correct_detections.extend(points)
        print(f"Found {len(points)} potential correct arrows")
    
    # Remove duplicates from correct detections
    unique_correct = []
    for point in correct_detections:
        is_duplicate = False
        for existing in unique_correct:
            distance = ((point[0] - existing[0])**2 + (point[1] - existing[1])**2)**0.5
            if distance < 40:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_correct.append(point)
    
    print(f"After deduplication: {len(unique_correct)} correct arrows")
    
    # PASS 2: Find incorrect arrows, but exclude areas near correct arrows
    print(f"PASS 2: Looking for incorrect arrows (threshold: {incorrect_threshold})")
    incorrect_detections = []
    
    for template_path in incorrect_template_paths:
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            continue
            
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= incorrect_threshold)
        points = list(zip(*locations[::-1]))
        
        print(f"Template {template_path}: found {len(points)} potential matches")
        incorrect_detections.extend(points)
    
    # Remove duplicates from incorrect detections
    unique_incorrect = []
    for point in incorrect_detections:
        is_duplicate = False
        for existing in unique_incorrect:
            distance = ((point[0] - existing[0])**2 + (point[1] - existing[1])**2)**0.5
            if distance < 40:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_incorrect.append(point)
    
    print(f"Before exclusion: {len(unique_incorrect)} incorrect arrows")
    
    # EXCLUSION: Remove incorrect arrows that are too close to correct arrows
    filtered_incorrect = []
    exclusion_distance = 35  # pixels
    
    for incorrect_point in unique_incorrect:
        too_close_to_correct = False
        
        for correct_point in unique_correct:
            distance = ((incorrect_point[0] - correct_point[0])**2 + (incorrect_point[1] - correct_point[1])**2)**0.5
            if distance < exclusion_distance:
                too_close_to_correct = True
                print(f"Excluding incorrect arrow at {incorrect_point} - too close to correct arrow at {correct_point} (distance: {distance:.1f})")
                break
        
        if not too_close_to_correct:
            filtered_incorrect.append(incorrect_point)
    
    print(f"After exclusion: {len(filtered_incorrect)} incorrect arrows")
    
    # Highlight incorrect arrows in red (only the filtered ones)
    for pt in filtered_incorrect:
        adjusted_x = pt[0] - 15
        adjusted_y = pt[1] - 15
        box_width = 45
        box_height = 45
        bgr_colour = (0, 0, 139)  # Red in BGR
        font_size = 1.5

        cv2.rectangle(result_image, (adjusted_x, adjusted_y), (adjusted_x + box_width, adjusted_y + box_height), bgr_colour, 3)
        cv2.putText(result_image, "X", (adjusted_x + 50, adjusted_y + 20), cv2.FONT_HERSHEY_SIMPLEX, font_size, bgr_colour, 4)
    
    return len(unique_correct), len(filtered_incorrect), result_image


def validate_board_arrows(image_path):
    """
    Validate that all arrows on a board are pointing in the correct direction.
    
    Args:
        image_path (str): Path to the board image
    
    Returns:
        tuple: (is_valid, message, correct_count, incorrect_count, annotated_image)
    """
    correct_count, incorrect_count, annotated_image = detect_arrow_orientations(image_path)
    
    if annotated_image is None:
        return False, "Could not load image", 0, 0, None
    
    if incorrect_count == 0:
        message = f"Valid board: All {correct_count} arrows pointing correctly"
        return True, message, correct_count, incorrect_count, annotated_image
    else:
        message = f"Invalid board: {incorrect_count} arrows pointing wrong direction"
        return False, message, correct_count, incorrect_count, annotated_image