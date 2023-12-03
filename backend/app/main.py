import os
import ssl
import urllib.request

import cv2
import numpy as np
import logging
import imageio
from skimage import io
from matplotlib import pyplot as plt

from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image, ImageFilter

#== Parameters =======================================================================
BLUR = 21
CANNY_THRESH_1 = 10
CANNY_THRESH_2 = 200
MASK_DILATE_ITER = 10
MASK_ERODE_ITER = 10
MASK_COLOR = (0.0,0.0,1.0) # In BGR format

app = FastAPI()

# SSL configuration for HTTPS requests
ssl._create_default_https_context = ssl._create_unverified_context

# CORS configuration: specify the origins that are allowed to make cross-site requests
origins = [
    "https://localhost:8080",
    "https://localhost:8080/",
    "http://localhost:8080",
    "http://localhost:8080/",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# A simple endpoint to verify that the API is online.
@app.get("/")
def home():
    return {"Test": "Online"}


@app.get("/process-image/{cldId}/{imgId}")
async def processImage(cldId: str, imgId: str, background_tasks: BackgroundTasks):
    """
    Endpoint to retrieve a processed version of an image.
    The image is fetched from a constructed URL and then processed.
    """
    img_path = f"app/bib/{imgId}.jpg"
    image_url = f"https://cmp.photoprintit.com/api/photos/{imgId}.org?size=original&errorImage=false&cldId={cldId}&clientVersion=0.0.1-medienVerDemo"

    download_image(image_url, img_path)
    #process_image(img_path)
    process_image_crop(img_path)

    # Schedule the image file to be deleted after the response is sent
    background_tasks.add_task(remove_file, img_path)

    # Send the processed image file as a response
    return FileResponse(img_path)


# Downloads an image from the specified URL and saves it to the given path.
def download_image(image_url: str, img_path: str):
    urllib.request.urlretrieve(image_url, img_path)


# Opens the image from the given path and applies a box blur effect.
def process_image(img_path: str):
    processedImage = Image.open(img_path)
    processedImage = processedImage.filter(ImageFilter.BoxBlur(10))
    processedImage.save(img_path)

def process_image_crop(img_path: str):
    processedImage = io.imread(img_path)
    gray = cv2.cvtColor(processedImage,cv2.COLOR_BGR2GRAY)
    
    #-- Edge detection -------------------------------------------------------------------
    edges = cv2.Canny(gray, CANNY_THRESH_1, CANNY_THRESH_2)
    edges = cv2.dilate(edges, None)
    edges = cv2.erode(edges, None)
    
    #-- Find contours in edges, sort by area ---------------------------------------------
    contour_info = []
    #_, contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    # Previously, for a previous version of cv2, this line was: 
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    # Thanks to notes from commenters, I've updated the code but left this note
    for c in contours:
        contour_info.append((
            c,
            cv2.isContourConvex(c),
            cv2.contourArea(c),
        ))
    contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
    max_contour = contour_info[0]
    
    #-- Create empty mask, draw filled polygon on it corresponding to largest contour ----
    # Mask is black, polygon is white
    mask = np.zeros(edges.shape)
    cv2.fillConvexPoly(mask, max_contour[0], (255))
    
    # #-- Smooth mask, then blur it --------------------------------------------------------
    mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
    mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
    mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
    mask_stack = np.dstack([mask]*3)    # Create 3-channel alpha mask
    
    #-- Blend masked processedImage into MASK_COLOR background --------------------------------------
    mask_stack  = mask_stack.astype('float32') / 255.0          # Use float matrices, 
    processedImage = processedImage.astype('float32') / 255.0                 #  for easy blending
 
    masked = (mask_stack * processedImage) + ((1-mask_stack) * MASK_COLOR) # Blend
    masked = (masked * 255).astype('uint8')                     # Convert back to 8-bit 
    
    # split image into channels
    c_red, c_green, c_blue = cv2.split(processedImage)

    # merge with mask got on one of a previous steps
    processedImage_a = cv2.merge((c_red, c_green, c_blue, mask.astype('float32') / 255.0))  

    #cv2.imwrite(img_path, processedImage_a*255.0)
    plt.imsave(img_path, processedImage_a)
    
   
# Deletes the file at the specified path.
def remove_file(path: str):
    os.unlink(path)


# Global exception handler that catches all exceptions not handled by specific exception handlers.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."},
    )
