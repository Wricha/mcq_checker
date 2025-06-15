import streamlit as st
import cv2
import numpy as np
import pandas as pd
import json
import os

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)
    return thresh

def detect_ticks(thresh_img, orig_img):
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ticks = []
    tick_img = orig_img.copy()
    
    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if 200 < area < 2000:  # Filtering by area
            x, y, w, h = cv2.boundingRect(cnt)
            ticks.append((x, y, w, h))
            
            # Draw tick detection
            cv2.rectangle(tick_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(tick_img, f"T{i}", (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Drawing center point
            center_x = x + w // 2
            center_y = y + h // 2
            cv2.circle(tick_img, (center_x, center_y), 3, (0, 255, 0), -1)
    
    return ticks, tick_img