import streamlit as st
import cv2
import numpy as np
import pandas as pd
import json
import os

def create_column_grid(image_shape, num_questions=6):
    """Create a simple 4-column grid layout"""
    height, width = image_shape[:2]
    
    print(f"🔧 Creating 4-column grid for image dimensions: {width}x{height}")
    
    # Define margins
    top_margin = int(height * 0.07)      
    bottom_margin = int(height * 0.05)   
    left_margin = int(width * 0.05)      
    right_margin = int(width * 0.05)     
    
    # Calculate usable area
    usable_height = height - top_margin - bottom_margin
    usable_width = width - left_margin - right_margin
    
    # Calculate cell dimensions
    question_height = usable_height // num_questions
    column_width = usable_width // 4  
    
    grid_cells = {}
    
    # Create grid cells for each question and option
    for q in range(1, num_questions + 1):
        # Calculate vertical position for this question
        question_y_start = top_margin + (q - 1) * question_height
        question_y_end = question_y_start + question_height
        
        # Add padding within each question row
        padding_y = int(question_height * 0.1)
        cell_y_start = question_y_start + padding_y
        cell_y_end = question_y_end - padding_y
        
        for col_idx, option in enumerate(['A', 'B', 'C', 'D']):
            # Calculate horizontal position for this column
            column_x_start = left_margin + col_idx * column_width
            column_x_end = column_x_start + column_width
            
            # Add padding within each column
            padding_x = int(column_width * 0.1)
            cell_x_start = column_x_start + padding_x
            cell_x_end = column_x_end - padding_x
            
            # Store the grid cell information
            grid_cells[(str(q), option)] = {
                'bounds': (cell_x_start, cell_y_start, cell_x_end, cell_y_end),
                'center': ((cell_x_start + cell_x_end) // 2, (cell_y_start + cell_y_end) // 2)
            }
            
            print(f"   Q{q}-{option}: ({cell_x_start}, {cell_y_start}) to ({cell_x_end}, {cell_y_end})")
    
    return grid_cells

def visualize_column_grid(image, grid_cells):
    """Visualize the 4-column grid on the image"""
    grid_img = image.copy()
    
    # Colors for different questions
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    
    # Group by question for consistent coloring
    question_colors = {}
    color_idx = 0
    
    for (qid, option), cell_info in grid_cells.items():
        if qid not in question_colors:
            question_colors[qid] = colors[color_idx % len(colors)]
            color_idx += 1
        
        color = question_colors[qid]
        x1, y1, x2, y2 = cell_info['bounds']
        
        # Draw grid cell
        cv2.rectangle(grid_img, (x1, y1), (x2, y2), color, 2)
        
        # Draw center point
        center_x, center_y = cell_info['center']
        cv2.circle(grid_img, (center_x, center_y), 5, color, -1)
        
        # Add label
        label = f"Q{qid}-{option}"
        cv2.putText(grid_img, label, (x1 + 5, y1 + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    return grid_img