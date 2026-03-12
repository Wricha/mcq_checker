# MCQ Checker
A model which marks the answersheet as per the correct answers in the sheets uploaded by the user

# Tech Stack
- OpenCv
- Flask
- Pandas
- Numpy

# Project Structure
mcq_checker/
├── app.py               # Flask web server and routing
├── gridCreation.py      # Detects and normalizes the answer grid
├── tickDetection.py     # Identifies filled bubbles/ticks
├── tickToOption.py      # Maps detections to answer labels
├── answer_key.json      # Configurable correct answers
├── templates/           # HTML templates for the UI
├── static/uploads/      # Stores uploaded answer sheet images
└── requirements.txt     # Python dependencies
