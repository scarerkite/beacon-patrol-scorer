import cv2
from arrow_detection import get_arrow_positions
import numpy as np

def detect_scorable_tiles(image_path):
    """
    Detect total tiles and count scorable (surrounded) tiles.
    
    Returns:
        tuple: (total_tiles, scorable_tiles, annotated_image)
    """
    correct_positions, _, image = get_arrow_positions(image_path)
    
    if image is None:
        return 0, 0, None, []
    
    estimated_size = _estimate_tile_size(correct_positions)
    if estimated_size is None:
        return 0, 0, image, []
    
    tile_boundaries = _estimate_tile_grid(correct_positions, estimated_size)
    
    # Count surrounded tiles
    scorable_count = 0
    scorable_boundaries = []
    
    for boundary in tile_boundaries:
        if _check_tile_surrounded(boundary, tile_boundaries):
            scorable_count += 1
            scorable_boundaries.append(boundary)

    for i, boundary in enumerate(tile_boundaries):
        is_surrounded = _check_tile_surrounded(boundary, tile_boundaries)
        print(f"Tile {i}: {boundary} -> Surrounded: {is_surrounded}")
    
    # Optionally annotate the scorable tiles
    annotated_image = _annotate_scorable_tiles(image, scorable_boundaries) if scorable_boundaries else image
    
    return len(tile_boundaries), scorable_count, annotated_image, scorable_boundaries

def _estimate_tile_size(arrow_positions):
    """Estimate tile sizes from arrow positions"""
    if len(arrow_positions) < 2:
        return None  # Can't estimate with fewer than 2 arrows
    
    # Find horizontal and vertical distances between arrows
    horizontal_distances = []
    vertical_distances = []
    
    for i, pos1 in enumerate(arrow_positions):
        for pos2 in arrow_positions[i+1:]:
            x_diff = abs(pos1[0] - pos2[0])
            y_diff = abs(pos1[1] - pos2[1])
            
            # If arrows are roughly horizontally aligned (small y difference)
            if y_diff < 20 and x_diff > 50:  # Adjust thresholds as needed
                horizontal_distances.append(x_diff)
            
            # If arrows are roughly vertically aligned (small x difference)
            if x_diff < 20 and y_diff > 50:
                vertical_distances.append(y_diff)
    
    # Filter out outliers by using smaller distances (nearest neighbors)
    if horizontal_distances:
        horizontal_distances.sort()
        # Use the smaller half of distances (nearest neighbors, not far connections)
        width = int(horizontal_distances[len(horizontal_distances)//4])  # Use 25th percentile instead of median
    else:
        width = None
        
    if vertical_distances:
        vertical_distances.sort()
        height = int(vertical_distances[len(vertical_distances)//4])  # Use 25th percentile instead of median
    else:
        height = None
    
    # If we only found one dimension, assume square tiles
    if width and not height:
        height = width
    elif height and not width:
        width = height
    
    return (width, height) if width and height else None
    
def _estimate_tile_grid(arrow_positions, estimated_tile_size):
    """Convert arrow positions to tile boundary rectangles"""
    if not arrow_positions or not estimated_tile_size:
        return []
    
    tile_width, tile_height = estimated_tile_size
    tile_boundaries = []
    
    # Adjustment offsets - tweak these values to align better
    arrow_offset_x = 30  # Move arrow position right by this amount
    arrow_offset_y = -10   # Move arrow position down by this amount
    
    for arrow_x, arrow_y in arrow_positions:
        # Adjust arrow position
        adjusted_arrow_x = arrow_x + arrow_offset_x
        adjusted_arrow_y = arrow_y + arrow_offset_y
        
        # Arrow is at top-right, so tile extends left and down from arrow
        tile_left = adjusted_arrow_x - tile_width
        tile_top = adjusted_arrow_y
        tile_right = adjusted_arrow_x
        tile_bottom = adjusted_arrow_y + tile_height
        
        # Store as (left, top, right, bottom) rectangle
        boundary = (tile_left, tile_top, tile_right, tile_bottom)
        tile_boundaries.append(boundary)
    
    print(f"Estimated tile size: {estimated_tile_size}")
    print(f"Generated {len(tile_boundaries)} tile boundaries")
    for i, boundary in enumerate(tile_boundaries):
        print(f"  Tile {i}: {boundary}")

    return tile_boundaries

def _check_tile_surrounded(tile_boundary, all_tile_boundaries):
    """Check if a tile has neighbors on all 4 sides"""
    left, top, right, bottom = tile_boundary
    tile_width = right - left
    tile_height = bottom - top
    
    # Define where adjacent tiles should be (exactly touching this tile)
    left_neighbor_area = (left - tile_width, top, left, bottom)
    right_neighbor_area = (right, top, right + tile_width, bottom)
    top_neighbor_area = (left, top - tile_height, right, top)
    bottom_neighbor_area = (left, bottom, right, bottom + tile_height)
    
    adjacent_areas = [left_neighbor_area, right_neighbor_area, top_neighbor_area, bottom_neighbor_area]
    
    neighbors_found = 0
    for target_area in adjacent_areas:
        # Check if any tile boundary overlaps significantly with this target area
        for other_boundary in all_tile_boundaries:
            if other_boundary != tile_boundary and _rectangles_overlap(target_area, other_boundary):
                neighbors_found += 1
                break  # Found a neighbor for this direction, move to next direction
    
    return neighbors_found == 4  # Surrounded if all 4 sides have neighbors

def _rectangles_overlap(rect1, rect2):
    """Check if two rectangles overlap significantly"""
    left1, top1, right1, bottom1 = rect1
    left2, top2, right2, bottom2 = rect2
    
    # Calculate overlap area
    overlap_left = max(left1, left2)
    overlap_top = max(top1, top2)
    overlap_right = min(right1, right2)
    overlap_bottom = min(bottom1, bottom2)
    
    # No overlap if coordinates don't make sense
    if overlap_left >= overlap_right or overlap_top >= overlap_bottom:
        return False
    
    # Calculate overlap percentage (to handle slight misalignments)
    overlap_area = (overlap_right - overlap_left) * (overlap_bottom - overlap_top)
    rect2_area = (right2 - left2) * (bottom2 - top2)
    
    # Consider it a match if overlap is significant (>70% of the target area)
    return overlap_area / rect2_area > 0.7

def _annotate_scorable_tiles(image, scorable_boundaries):
    """Draw highlights around scorable tiles"""
    if not scorable_boundaries:
        return image
    
    # For now, just return the original image
    # TODO: Add visual annotations later
    return image

def visualize_tile_boundaries(image_path, save_path=None):
    """Draw tile boundaries on image for visual verification"""
    correct_positions, _, image = get_arrow_positions(image_path)
    
    if image is None:
        print(f"Could not load image: {image_path}")
        return None
    
    estimated_size = _estimate_tile_size(correct_positions)
    if estimated_size is None:
        print("Could not estimate tile size")
        return None
    
    tile_boundaries = _estimate_tile_grid(correct_positions, estimated_size)
    
    # Draw boundaries on image
    result_image = image.copy()
    
    for i, (left, top, right, bottom) in enumerate(tile_boundaries):
        # Draw tile boundary rectangle in green
        cv2.rectangle(result_image, (int(left), int(top)), (int(right), int(bottom)), (0, 255, 0), 2)
        
        # Draw arrow position as a red dot (top-right corner of tile)
        cv2.circle(result_image, (int(right), int(top)), 5, (0, 0, 255), -1)
        
        # Label each tile with a number
        cv2.putText(result_image, str(i), (int(left + 10), int(top + 30)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    # Save or display
    if save_path:
        cv2.imwrite(save_path, result_image)
        print(f"Saved visualization to {save_path}")
    else:
        cv2.imshow("Tile Boundaries", result_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return result_image


if __name__ == "__main__":
    image_path = "test_images/valid_boards/board_7.jpg"  # Replace with your actual image path

    print("=== ARROW DETECTION DEBUG ===")
    from arrow_detection import get_arrow_positions
    correct_positions, incorrect_positions, image = get_arrow_positions(image_path)
    print(f"Found {len(correct_positions)} correct arrows")
    print(f"Found {len(incorrect_positions)} incorrect arrows")
    print("Arrow positions:", correct_positions)

    if len(correct_positions) < 23:
        print(f"PROBLEM: Expected 23 arrows, only found {len(correct_positions)}")
        print("Possible issues:")
        print("- Arrow template matching threshold too high")
        print("- Some arrows have different appearance")
        print("- Arrows partially obscured or at different angles")
    
    print("=== TILE DETECTION DEBUG ===")
    
    # Run the full detection with debug output
    total_tiles, scorable_count, annotated_image, scorable_boundaries = detect_scorable_tiles(image_path)
    print(f"\nSummary: {total_tiles} total tiles, {scorable_count} scorable")
    
    print("\n=== VISUALIZING TILE BOUNDARIES ===")
    
    # Show the visual representation
    visualize_tile_boundaries(image_path)