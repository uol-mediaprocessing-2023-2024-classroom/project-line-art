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

from segment_anything import SamPredictor, sam_model_registry, SamAutomaticMaskGenerator
import torch
from skimage import filters
from fastapi.middleware.cors import CORSMiddleware
from numpy import asarray
from PIL import Image, ImageOps

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
    CORSMiddleware,
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

sam_checkpoint = "/Users/alinameyer/Documents/Master Ol/03 Medienverarbeitung/LineArt/backend/app/sam_vit_h_4b8939.pth"
model_type = "vit_h"

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)

predictor = SamPredictor(sam)
mask_generator = SamAutomaticMaskGenerator(sam)

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
    remove_background(img_path)
    get_segments(img_path)
    #remove_background('segments_image.png')
    get_lines_from_segmenst(img_path)

    # Schedule the image file to be deleted after the response is sent
    background_tasks.add_task(remove_file, img_path)

    # Send the processed image file as a response
    return FileResponse(img_path)

def get_segments(img_path: str):
    img = cv2.imread('new_img.png')
    masks = mask_generator.generate(img)
    anns = show_anns(masks)
    plt.imsave(img_path, anns)
    
    temp = 255 * anns # Now scale by 255
    segments = temp.astype(np.uint8)
    cv2.imwrite('segments_image.png', segments)

def get_lines_from_segmenst(img_path: str):
    img = cv2.imread('segments_image.png')
    # Setting All parameters 
    t_lower = 100  # Lower Threshold
    t_upper = 500  # Upper threshold 
    aperture_size = 5  # Aperture size 
    kernel = np.ones((4,4), np.uint8) 
    
    # Applying the Canny Edge filter 
    # with Custom Aperture Size 
    edges = cv2.Canny(img, t_lower, t_upper,  
                    apertureSize=aperture_size) 
    edges = cv2.dilate(edges, kernel)
    edges = cv2.dilate(edges, kernel)
    edges = cv2.erode(edges, kernel)
    cv2.imwrite('edges_image.png', edges)
    plt.imsave(img_path, edges)

# Downloads an image from the specified URL and saves it to the given path.
def download_image(image_url: str, img_path: str):
    urllib.request.urlretrieve(image_url, img_path)


def remove_background(img_path: str):
    img = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)

    best_mask = get_best_mask(img)

    # Assuming 'image' is your original image and 'segmentation_mask' is the mask image
    binary_mask = np.where(best_mask > 0.5, 1, 0)

    # Create a new image with the same size and RGBA format
    new_image = np.zeros((img.shape[0], img.shape[1], 4))

    # Use the binary mask to combine the original image and the transparency
    new_image[..., :3] = img * binary_mask[..., np.newaxis]
    new_image[..., 3] = binary_mask * 255


    # Save the result as a PNG file
    cv2.imwrite('new_img.png', new_image)
    new_image = new_image / 255.0

    return new_image
    #plt.imsave(img_path, new_image)


def get_best_mask(img: Image):
    array_image = np.asarray(img)

    predictor = SamPredictor(sam)
    predictor.set_image(array_image)

    input_point = np.array([[600, 400], [525, 600], [425, 600]])
    input_label = np.array([1, 1, 0])

    masks, scores, logits = predictor.predict(
    multimask_output=True,
    point_coords=input_point,
    point_labels=input_label,
    )
    masks.shape 
    best_mask = masks
    currentScore = 0

    for i, (mask, score) in enumerate(zip(masks, scores)):
        if (score > currentScore):
            currentScore = score
            best_mask = mask

    return best_mask
            
def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)

def show_points(coords, labels, ax, marker_size=375):
    pos_points = coords[labels==1]
    neg_points = coords[labels==0]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)

def show_box(box, ax):
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0,0,0,0), lw=2))

def show_anns(anns):
    if len(anns) == 0:
        return
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    ax = plt.gca()
    ax.set_autoscale_on(False)

    i = np.ones((sorted_anns[0]['segmentation'].shape[0], sorted_anns[0]['segmentation'].shape[1], 4))
    i[:,:,3] = 0
    for ann in sorted_anns:
        m = ann['segmentation']
        color_mask = np.concatenate([np.random.random(3), [0.99]])
        i[m] = color_mask
    #ax.imshow(i)
    return i


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
    
def process_image_contours(img_path: str):
    processedImage = io.imread(img_path)

    gray = cv2.cvtColor(processedImage, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(
        binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    drawing = np.zeros((gray.shape[0], gray.shape[1], 3), dtype=np.uint8)
    CountersImg = cv2.drawContours(drawing, contours, -1, (255, 255, 0), 3)

    # save to disk
    plt.imsave(img_path, CountersImg)

   
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
