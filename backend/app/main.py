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
from numpy import asarray
from PIL import Image, ImageOps

import mediapipe as mp
import random


#== Parameters =======================================================================
BLUR = 21
CANNY_THRESH_1 = 10
CANNY_THRESH_2 = 200
MASK_DILATE_ITER = 10
MASK_ERODE_ITER = 10
MASK_COLOR = (1.0,1.0,1.0)

app = FastAPI()

# SSL configuration for HTTPS requests
ssl._create_default_https_context = ssl._create_unverified_context

# CORS configuration: specify the origins that are allowed to make cross-site requests
origins = [
    "https://localhost:8080",
    "http://localhost:8080",
    "https://localhost:8081",
    "http://localhost:8081",
    "https://localhost:8082",
    "http://localhost:8082",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_path = './app/pose_landmarker_lite.task'

sam_checkpoint = "./SamCheckpoint/sam_vit_h_4b8939.pth"
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
    
@app.get("/process-image/{cldId}/{imgId}/{currentOptionContours}/{currentOptionSegments}/{selectedColorContours}/{selectedColorSegments}")
async def processImage(cldId: str, imgId: str, currentOptionContours: str, currentOptionSegments: str, selectedColorContours: str, selectedColorSegments: str, background_tasks: BackgroundTasks):
    """
    Endpoint to retrieve a processed version of an image.
    The image is fetched from a constructed URL and then processed.
    """
    img_path = f"app/bib/{imgId}.jpg"
    image_url = f"https://cmp.photoprintit.com/api/photos/{imgId}.org?size=original&errorImage=false&cldId={cldId}&clientVersion=0.0.1-medienVerDemo"

    mainColor = get_main_color(img_path)
    download_image(image_url, img_path)
    remove_background(img_path)
    masks = get_segments(img_path)
    m = get_random_mask(masks)
    print(m['segmentation'])
    if currentOptionContours == "NoColor":
        #remove_background('segments_image.png')
        get_lines_from_segments(img_path, hex_to_rgb("000000"))
    if currentOptionContours == "Imagebased":
        #remove_background('segments_image.png')
        get_lines_from_segments(img_path, mainColor)
    if currentOptionContours == "SelectColorContours":
        get_lines_from_segments(img_path, hex_to_rgb(selectedColorContours))


    if currentOptionSegments == "NoColor":    
        i = cv2.imread("contures_img.png")
        plt.imsave(img_path, i)
    elif currentOptionSegments ==  "Imagebased":
        print("imagebased")
        color_segments(img_path,mainColor, masks)
    elif currentOptionSegments ==  "Imagebased":
        print("selected color")
        color_segments(img_path,hex_to_rgb(selectedColorSegments), masks)



    # Schedule the image file to be deleted after the response is sent
    #background_tasks.add_task(remove_file, img_path)

    # Send the processed image file as a response
    return FileResponse(img_path)

def color_segments(img_path:str, color: object, masks: object):
    print("color Segments")
    mask = get_random_mask(masks)
    i = cv2.imread("contures_img.png")
    
    # Farbe des Segments ändern (hier: Rot)
    #mask[:, :] = rgb_color

    # Das eingefärbte Segment zurück ins Bild einfügen
   # bild[startpunkt[1]:endpunkt[1], startpunkt[0]:endpunkt[0]] = segment
    #plt.imshow(i)
    
    #r = show_mask(mask['segmentation'], plt.gca())
    c = np.array([30/255, 144/255, 255/255, 1])

    mas_array = mask['segmentation']
    h, w = mas_array.shape[-2:]
    mask_image = mas_array.reshape(h, w, 1) * c.reshape(1, 1, -1)
    temp = 255 * mask_image # Now scale by 255
    s = temp.astype(np.uint8)
    cv2.imwrite('test_seg.png', s)

    test_one = Image.open('contures_img.png')
    test_two = Image.open('test_seg.png')
    x = Image.fromarray(mask_image, 'RGB')
    Image.blend(test_one, test_two, 0.5).save('result_seg.png')
    final_result = cv2.imread('result_seg.png')
    plt.imsave(img_path, final_result)



def get_random_mask(masks: object):
    choice = random.choice(masks)
    print(choice)
    return choice

def get_segments(img_path: str):
    img = cv2.imread('new_img.png')
    masks = mask_generator.generate(img)
    anns = show_anns(masks)
    plt.imsave(img_path, anns)
    
    temp = 255 * anns # Now scale by 255
    segments = temp.astype(np.uint8)
    cv2.imwrite('segments_image.png', segments)
    return masks

def get_lines_from_segments(img_path: str, selectedColor: str):
    img = cv2.imread('segments_image.png')
    # Setting All parameters 
    t_lower = 100  # Lower Threshold
    t_upper = 500  # Upper threshold 
    aperture_size = 5  # Aperture size 
    kernel = np.ones((4,4), np.uint8) 
    NEW_LINE_COLOR = selectedColor  # Set the desired color for lines
    NEW_LINE_COLOR_normalized = [val / 255.0 for val in NEW_LINE_COLOR]
    
    # Applying the Canny Edge filter 
    # with Custom Aperture Size 
    edges = cv2.Canny(img, t_lower, t_upper,  
                    apertureSize=aperture_size) 
    #edges = cv2.dilate(edges, kernel)
    #edges = cv2.erode(edges, kernel)
    
    # Stack arrays in the depth sequence (along the third axis).
    mask_stack = np.dstack([edges]*3)    # Create 3-channel alpha mask

    #-- Blend masked img into MASK_COLOR background --------------------------------------
    mask_stack  = mask_stack.astype('float32') / 255.0          # Use float matrices, 
    img         = img.astype('float32') / 255.0                 #  for easy blending

    masked = (mask_stack * NEW_LINE_COLOR_normalized) + ((1-mask_stack) * MASK_COLOR) # Blend 

    cv2.imwrite('edges.png', edges)
    #plt.imsave(img_path, masked)
    plt.imsave("contures_img.png", masked)

# Downloads an image from the specified URL and saves it to the given path.
def download_image(image_url: str, img_path: str):
    urllib.request.urlretrieve(image_url, img_path)

def remove_background(img_path: str):
    img = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)

    best_mask = get_best_mask(img_path, img)

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

def get_main_color(image_path):
     # Bild öffnen
    image = io.imread(image_path)

    # Bild in ein NumPy-Array konvertieren
    image_array = np.array(image)

    # Die Form des Arrays ändern, um die Pixel als Flachliste zu erhalten
    flattened_image_array = image_array.reshape((-1, 3))

    # Die Hauptfarbe finden, indem der Durchschnitt der RGB-Werte berechnet wird
    main_color = np.mean(flattened_image_array, axis=0)
    
    # Konvertiere die Hauptfarbe in eine Liste von Ganzzahlen
    main_color_list = main_color.astype(int).tolist()

    return main_color_list

def hex_to_rgb(hex_color):
    # Extrahiere die Hexadezimalzahlen für Rot, Grün und Blau
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)

    return [red, green, blue]

def get_best_mask(img_path: str, img: Image):
    array_image = np.asarray(img)

    predictor = SamPredictor(sam)
    predictor.set_image(array_image)

    input_point = get_inpupt_points(img_path) 
    input_label = np.array([1, 1, 1])

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

def get_inpupt_points(img_path: str):
    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    model_path = 'app/pose_landmarker_lite.task'

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.IMAGE)

    with PoseLandmarker.create_from_options(options) as landmarker:
        # The landmarker is initialized. Use it here.
        # Load the input image from an image file.
        mp_image = mp.Image.create_from_file(img_path) 
        print(mp_image.width) 
        # Perform pose landmarking on the provided single image.
        # The pose landmarker must be created with the image mode.
        pose_landmarker_result = landmarker.detect(mp_image)          

    img = Image.open(img_path)
    width, height = img.size 

    nose = pose_landmarker_result.pose_landmarks[0][0]
    nose_x = nose.x * width
    nose_y = nose.y * height

    shoulder = pose_landmarker_result.pose_landmarks[0][12]
    shoulder_x = shoulder.x * width
    shoulder_y = shoulder.y * height

    hip = pose_landmarker_result.pose_landmarks[0][23]
    hip_x =hip.x * width
    hip_y = hip.y * height

    input_points = np.array([[nose_x, nose_y], [shoulder_x,shoulder_y], [hip_x, hip_y]])
    return input_points


def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)
    return ax


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
