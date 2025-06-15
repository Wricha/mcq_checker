from flask import Flask, render_template, request, redirect, send_file
import cv2
import numpy as np
import pandas as pd
import json
import os
import uuid

from tickDetection import preprocess_image, detect_ticks
from tickToOption import assign_ticks_to_grid_nearest, draw_final_results
from gridCreation import create_column_grid, visualize_column_grid

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        num_questions = int(request.form.get("num_questions", 6))
        file = request.files.get("image")
        if file:
            # Save image
            filename = f"{uuid.uuid4().hex}_{file.filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Load answer key
            try:
                with open("answer_key.json", "r") as f:
                    answer_key = json.load(f)
            except FileNotFoundError:
                answer_key = {"answers": {}}

            # Read image
            image = cv2.imread(filepath)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Grid generation
            grid_cells = create_column_grid(image.shape, num_questions)
            grid_img = visualize_column_grid(image.copy(), grid_cells)
            grid_path = os.path.join(UPLOAD_FOLDER, f"grid_{filename}")
            cv2.imwrite(grid_path, grid_img)

            # Tick detection
            thresh = preprocess_image(image.copy())
            ticks, tick_img = detect_ticks(thresh, image.copy())
            tick_centers = [(x + w // 2, y + h // 2) for (x, y, w, h) in ticks]

            tick_img_path = os.path.join(UPLOAD_FOLDER, f"ticks_{filename}")
            cv2.imwrite(tick_img_path, tick_img)

            # Assign to nearest grid cell
            detected_answers, tick_assignments = assign_ticks_to_grid_nearest(tick_centers, grid_cells, 150)

            final_result_img = draw_final_results(image.copy(), grid_cells, tick_assignments, tick_centers)
            final_result_path = os.path.join(UPLOAD_FOLDER, f"final_{filename}")
            cv2.imwrite(final_result_path, final_result_img)

            # Generate results table
            results_data = []
            correct = 0
            total = len(answer_key.get("answers", {}))
            for q in range(1, num_questions + 1):
                qid = str(q)
                student_ans = detected_answers.get(qid, "Not Detected")
                correct_ans = answer_key["answers"].get(qid, "N/A")
                is_correct = student_ans == correct_ans and correct_ans != "N/A"
                if is_correct:
                    correct += 1
                status = "Correct" if is_correct else ("Wrong" if correct_ans != "N/A" else "No Key")
                results_data.append({
                    "Question": qid,
                    "Detected": student_ans,
                    "Correct": correct_ans,
                    "Status": status
                })

            score = (correct / total * 100) if total > 0 else None

            return render_template("results.html",
                                   original=filename,
                                   grid=grid_path,
                                   ticks=tick_img_path,
                                   final=final_result_path,
                                   results=results_data,
                                   score=score,
                                   correct=correct,
                                   total=total)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
