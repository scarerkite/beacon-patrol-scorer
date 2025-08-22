#!/usr/bin/env python3
"""
Debug script for Beacon Patrol scoring pipeline
Run this to diagnose scoring issues
"""

from tile_analyzer import detect_scorable_tiles
from scored_objects_detector import calculate_board_score
from arrow_detection import validate_board_arrows
import os

def debug_image(image_path):
    """Debug a single image through the entire pipeline"""
    print(f"\n{'='*60}")
    print(f"DEBUGGING: {image_path}")
    print(f"{'='*60}")
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"❌ ERROR: File does not exist: {image_path}")
        return
    
    print(f"✅ File exists: {image_path}")
    
    # Step 1: Arrow validation
    print(f"\n--- Step 1: Arrow Validation ---")
    try:
        is_valid, message, correct_count, incorrect_count, annotated_image = validate_board_arrows(image_path)
        print(f"Valid arrows: {is_valid}")
        print(f"Message: {message}")
        print(f"Correct arrows: {correct_count}, Incorrect: {incorrect_count}")
    except Exception as e:
        print(f"❌ Arrow validation failed: {e}")
        return
    
    if not is_valid:
        print("❌ Board invalid due to arrow orientation - stopping here")
        return
    
    # Step 2: Tile detection
    print(f"\n--- Step 2: Tile Detection ---")
    try:
        total_tiles, scorable_count, annotated_image, scorable_boundaries = detect_scorable_tiles(image_path)
        print(f"Total tiles found: {total_tiles}")
        print(f"Scorable tiles found: {scorable_count}")
        print(f"Scorable boundaries: {len(scorable_boundaries) if scorable_boundaries else 0}")
        
        if scorable_count == 0:
            print("❌ No scorable tiles found - this will result in 0 score")
            return
            
    except Exception as e:
        print(f"❌ Tile detection failed: {e}")
        return
    
    # Step 3: Complete scoring
    print(f"\n--- Step 3: Complete Scoring ---")
    try:
        result = calculate_board_score(image_path)
        print(f"Final score: {result}")
    except Exception as e:
        print(f"❌ Scoring failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n✅ SUCCESS: Debugging complete for {image_path}")

def debug_arrow_detection_issue(image_path):
    """Debug arrow detection specifically for images that should be valid"""
    print(f"\n🎯 ARROW DETECTION DEBUG: {image_path}")
    print(f"{'='*50}")
    
    from arrow_detection import validate_board_arrows
    import cv2
    
    try:
        is_valid, message, correct_count, incorrect_count, annotated_image = validate_board_arrows(image_path)
        
        print(f"Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
        print(f"Message: {message}")
        print(f"Correct arrows: {correct_count}")
        print(f"Incorrect arrows: {incorrect_count}")
        
        # Save annotated image to see what's being marked as wrong
        if annotated_image is not None:
            debug_filename = f"debug_arrows_{os.path.basename(image_path)}"
            cv2.imwrite(debug_filename, annotated_image)
            print(f"💾 Saved annotated image: {debug_filename}")
            print("   Look at this image to see which arrows are marked as incorrect")
        
        if not is_valid:
            print("🔧 SUGGESTION: Try lowering arrow detection thresholds")
            print("   In arrow_detection.py, change:")
            print("   correct_threshold=0.8 → correct_threshold=0.75")
            print("   incorrect_threshold=0.8 → incorrect_threshold=0.85")
            
    except Exception as e:
        print(f"❌ Arrow detection failed: {e}")

def main():
    """Debug multiple test images"""
    
    # List of test images to check
    test_images = [
        "test_images/valid_boards/7_tiles_blue.jpg",
        "test_images/valid_boards/board_7.jpg", 
        "test_images/valid_boards/12_tiles.jpg",
        "test_images/valid_boards/14_tiles.jpg",
        "test_images/valid_boards/board_16.jpg",
        "test_images/valid_boards/board_20.jpg",
    ]
    
    print("🔍 BEACON PATROL SCORING DEBUG")
    print("This will test each image through the complete pipeline\n")
    
    # First, specifically debug the arrow detection issue
    print("STEP 1: Arrow Detection Debug")
    debug_arrow_detection_issue("test_images/valid_boards/12_tiles.jpg")
    
    print(f"\n{'='*60}")
    print("STEP 2: Full Pipeline Debug")
    print(f"{'='*60}")
    
    for image_path in test_images:
        debug_image(image_path)
    
    print(f"\n{'='*60}")
    print("DEBUG COMPLETE")
    print("If all images show ❌ errors, there's a fundamental issue.")
    print("If some work and others don't, it's likely image-specific.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()