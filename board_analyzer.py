from PIL import Image
import cv2
import numpy as np
from arrow_detection import validate_board_arrows 

def _is_blue(pixel):
    r, g, b = pixel

    return b > r and b > g and b > 100

def _is_valid_image_size(image_input):
    if hasattr(image_input, 'size'):
        width, height = image_input.size
    else:
        # It's a file path
        with Image.open(image_input) as img:
            width, height = img.size
    
    return 200 <= width <= 4000 and 200 <= height <= 4000

def _check_board_colors(image_input):
    """Validate that image has enough blue to be a Beacon Patrol board"""
    # Convert to PIL Image if needed
    if hasattr(image_input, 'read'):
        image_input.seek(0)
        img = Image.open(image_input)
    elif isinstance(image_input, str):
        img = Image.open(image_input)
    else:
        img = image_input

    img = img.convert("RGB")
    pixels = list(img.getdata())
    sampled_pixels = pixels[::50]  # Every 50th pixel

    blue_count = 0
    for pixel in sampled_pixels:
        if _is_blue(pixel):
            blue_count += 1

    blue_percentage = blue_count / len(sampled_pixels)
    return blue_percentage > 0.5  # 50% threshold

def _calculate_score(image_path):
    """Calculate the actual game score (placeholder for now)"""
    # TODO: Implement actual tile detection and scoring
    return 42

def _get_rank_for_score(score):
    # TODO: Implement comparison of score to rules
    return "Sailors"

def analyze_complete_board(image_input, save_path=None):
    """
    Complete board analysis pipeline with fail-fast validation.
    
    Args:
        image_input: PIL Image object, BytesIO object, or file path
        save_path: File path needed for arrow detection (optional)
    
    Returns:
        dict: {
            'is_valid': bool,
            'score': int,
            'rank': str,
            'errors': list,
            'failed_at': str (only if invalid),
            'details': dict (additional analysis info)
        }
    """
    
    # Check 1: Basic image size validation
    try:
        if not _is_valid_image_size(image_input):
            return {
                'is_valid': False,
                'errors': ['Image too small (minimum 200x200) or too large (maximum 4000x4000)'],
                'failed_at': 'size_check'
            }
    except Exception as e:
        return {
            'is_valid': False,
            'errors': ['Could not read image file'],
            'failed_at': 'image_read'
        }
    
    # Check 2: Color validation (blue water check)
    try:
        if not _check_board_colors(image_input):
            return {
                'is_valid': False,
                'errors': ['This does not look like a Beacon Patrol game. Please upload a different photo.'],
                'failed_at': 'color_check'
            }
    except Exception as e:
        return {
            'is_valid': False,
            'errors': ['Error analyzing image colors'],
            'failed_at': 'color_check'
        }
    
    # Check 3: Arrow orientation validation (if we have a file path)
    arrow_details = {}
    if save_path:
        try:
            is_valid_arrows, message, correct_count, incorrect_count, annotated_image = validate_board_arrows(save_path)
            
            if not is_valid_arrows:
                return {
                    'is_valid': False,
                    'errors': [message],
                    'failed_at': 'arrow_check',
                    'details': {
                        'correct_arrows': correct_count,
                        'incorrect_arrows': incorrect_count
                    },
                    'annotated_image': annotated_image
                }
            
            arrow_details = {
                'correct_arrows': correct_count,
                'incorrect_arrows': incorrect_count,
                'arrow_message': message
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'errors': ['Error validating arrow orientations'],
                'failed_at': 'arrow_check'
            }
    
    # All hoops passed - calculate score
    try:
        score = _calculate_score(save_path)
        rank = _get_rank_for_score(score)
        
        return {
            'is_valid': True,
            'score': score,
            'rank': rank,
            'errors': [],
            'details': {
                'passed_all_checks': True,
                **arrow_details
            },
            'annotated_image': annotated_image if save_path else None
        }
        
    except Exception as e:
        return {
            'is_valid': False,
            'errors': ['Error calculating final score'],
            'failed_at': 'scoring'
        }
