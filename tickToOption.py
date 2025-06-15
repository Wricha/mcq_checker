import streamlit as st
import cv2
import numpy as np
import pandas as pd
import json
import os

def calculate_distance_to_cell(tick_x, tick_y, cell_bounds):
    x1, y1, x2, y2 = cell_bounds
    
    # If the tick is inside the cell, distance is 0
    if x1 <= tick_x <= x2 and y1 <= tick_y <= y2:
        return 0.0
    
    # Calculate distance to the nearest edge of the rectangle
    dx = max(0, max(x1 - tick_x, tick_x - x2))
    dy = max(0, max(y1 - tick_y, tick_y - y2))
    
    return (dx ** 2 + dy ** 2) ** 0.5

def assign_ticks_to_grid_nearest(tick_centers, grid_cells, max_distance=150):
    
    answers = {}
    tick_assignments = {}
    
    print(f"🔍 Processing {len(tick_centers)} tick centers against {len(grid_cells)} grid cells")
    print(f"📏 Maximum assignment distance: {max_distance}px")
    
    for tick_idx, (tick_x, tick_y) in enumerate(tick_centers):
        print(f"\n🎯 Tick {tick_idx} at ({tick_x}, {tick_y})")
        
        best_match = None
        best_distance = float('inf')
        
        # Check distance to ALL grid cells
        for (qid, option), cell_info in grid_cells.items():
            distance = calculate_distance_to_cell(tick_x, tick_y, cell_info['bounds'])
            
            print(f" Distance to Q{qid}-{option}: {distance:.1f}px")
            
            if distance < best_distance and distance <= max_distance:
                best_distance = distance
                best_match = (qid, option, distance)
        
        if best_match:
            qid, option, distance = best_match
            
            # Only assign if this question doesn't already have a closer answer
            if qid not in answers or distance < tick_assignments.get(qid, {}).get('distance', float('inf')):
                # If this question already has an assignment, check if new one is significantly closer
                if qid in answers:
                    old_distance = tick_assignments[qid]['distance']
                    print(f"   🔄 Q{qid} already assigned to {answers[qid]} (distance: {old_distance:.1f})")
                    print(f"   🔄 New assignment {option} has distance: {distance:.1f}")
                    
                    # Only reassign if new tick is significantly closer (at least 20px difference)
                    if distance < old_distance - 20:
                        print(f" Reassigning Q{qid} from {answers[qid]} to {option}")
                        answers[qid] = option
                        tick_assignments[qid] = {
                            'tick_idx': tick_idx,
                            'tick_pos': (tick_x, tick_y),
                            'distance': distance,
                            'option': option
                        }
                    else:
                        print(f" Keeping existing assignment (not significantly closer)")
                else:
                    answers[qid] = option
                    tick_assignments[qid] = {
                        'tick_idx': tick_idx,
                        'tick_pos': (tick_x, tick_y),
                        'distance': distance,
                        'option': option
                    }
                    print(f" Assigned Q{qid} = {option} (distance: {distance:.1f})")
        else:
            print(f"  No assignment (closest distance > {max_distance}px)")
    
    return answers, tick_assignments

def draw_final_results(image, grid_cells, tick_assignments, all_tick_centers):

    result_img = image.copy()
    
    # Colors for different questions
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    question_colors = {}
    color_idx = 0
    
    # Draw all grid cells
    for (qid, option), cell_info in grid_cells.items():
        if qid not in question_colors:
            question_colors[qid] = colors[color_idx % len(colors)]
            color_idx += 1
        
        color = question_colors[qid]
        x1, y1, x2, y2 = cell_info['bounds']
        
        # Check if this cell is selected
        is_selected = (qid in tick_assignments and 
                      tick_assignments[qid]['option'] == option)
        
        # Draw grid cell (highlighted if selected)
        thickness = 4 if is_selected else 2
        
        if is_selected:
            # Fill selected cells
            overlay = result_img.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
            cv2.addWeighted(overlay, 0.3, result_img, 0.7, 0, result_img)
        
        cv2.rectangle(result_img, (x1, y1), (x2, y2), color, thickness)
        
        # Add label
        label = f"Q{qid}-{option}"
        if is_selected:
            label += " ✓"
        
        font_scale = 0.7 if is_selected else 0.5
        thickness = 2 if is_selected else 1
        cv2.putText(result_img, label, (x1 + 5, y1 + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
    
    # Draw tick centers and connection lines
    for i, (tick_x, tick_y) in enumerate(all_tick_centers):
        assigned_info = None
        for qid, assignment in tick_assignments.items():
            if assignment['tick_idx'] == i:
                assigned_info = (qid, assignment)
                break
        
        if assigned_info:
            qid, assignment = assigned_info
            color = question_colors[qid]
            
            # Draw tick center
            cv2.circle(result_img, (tick_x, tick_y), 8, color, -1)
            cv2.circle(result_img, (tick_x, tick_y), 10, (255, 255, 255), 2)
            
            # Draw connection line to assigned cell
            cell_center = grid_cells[(qid, assignment['option'])]['center']
            cv2.line(result_img, (tick_x, tick_y), cell_center, color, 2)
            
            # Add distance label
            mid_x = (tick_x + cell_center[0]) // 2
            mid_y = (tick_y + cell_center[1]) // 2
            distance_text = f"{assignment['distance']:.0f}px"
            cv2.putText(result_img, distance_text, (mid_x, mid_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        else:
            # Unassigned tick
            cv2.circle(result_img, (tick_x, tick_y), 5, (0, 0, 255), -1)
    
    return result_img