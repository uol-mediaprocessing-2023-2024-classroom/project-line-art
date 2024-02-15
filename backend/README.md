# Backend Demo

## Setup
1. Python is required and can be downloaded here: https://www.python.org/downloads/ (I am using Python 3.10)
2. Open the repository directory and execute this command in the terminal:
```
pip install -r .\requirements.txt
```
3. Downloading SAM from "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth" and moving it in the directory: backend/SamCheckpoint
## Starting the App
```
uvicorn app.main:app --reload
```

## About the Backend
<p>This application serves as a simple Python-based backend for a web app.</p>
<p>The only endpoint ("/get-blur") adds a blur to an image and responds with the edited image.</p>

Docs: https://fastapi.tiangolo.com/tutorial/