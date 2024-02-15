
# LineArt
Group: Alina Meyer, John-Uwe Riecken, Talea Schweers

This project is about processing images so that they look hand-drawn. This type of line art is the goal of this project.
The goal of the project is that a user can have an image edited through a user-friendly web app to make it look hand-drawn without losing the important aspects of the image.

# Backend

## Setup
1. Python is required and can be downloaded here: https://www.python.org/downloads/ (We are using Python 3.10)
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

<p></p>

# Frontend

## Setup

1. First, Node.js must be installed. For Windows, an installer can be used: https://nodejs.org/en/download/
2. Now, the dependencies can be installed: ```npm install```
3. (If an error is displayed when starting: ```npm install @vue/cli-service -g```)

## Compile and Start
```npm run serve```
<br>
After starting, the site can be accessed via localhost.
<br>

## About the App
<p>This repository contains the frontend of the simple demo app. The frontend uses Vue and the Vuetify framework (Version 2), which offers many functionalities as well as pre-made Vue components.</p>
<p>To use the app, a CEWE myPhotos account is required (https://www.cewe-myphotos.com/en-gb/). In the 'Username' and 'Password' fields of the app, the username and password of the CEWE account must be entered, after which the photos from the account can be loaded into the app using 'Load Images'.</p>
<p>The "Apply Blur" button sends a request that sends the selected image to the local backend (located in this repository: https://github.com/uol-mediaprocessing-2023-2024-classroom/web_app_demo_backend) and waits for a response.
<br>

<strong>Important</strong>: Before shutting down the server, you should log out; otherwise, the client remains logged into the CEWE API without the necessary clId to log out.
This will happen automatically after one hour, but until then, you cannot log in again.</p>

