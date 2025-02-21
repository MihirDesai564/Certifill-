import cv2
import os
import numpy as np 
import unicodedata
from PIL import Image, ImageDraw, ImageFont


font_cache = {}

font_map ={
    "devnagari": ["NotoSansDevanagari-Regular.ttf", "mangal.ttf", "DejaVuSans.ttf"],
    "english": ["arial.ttf", "times.ttf", "DejaVuSans.ttf"],
    "mixed": ["NotoSansDevanagari-Regular.ttf", "arialuni.ttf", "DejaVuSans.ttf"]
}

def normalize_text(text):
    return unicodedata.normalize("NFC", text)

def get_font(font_path, size):
    key = (font_path, size)
    if key not in font_cache:
        font_cache[key] = ImageFont.truetype(font_path, size)
    return font_cache[key]

def detect_script(text):
    has_devnagari = any(0x0900 <= ord(char) <= 0x097F for char in text)
    has_latin = any(0x0041 <= ord(char) <= 0x007A for char in text)
    if has_devnagari and has_latin:
        return "mixed"
    elif has_devnagari:
        return "devnagari"
    else:
        return "english"
    
def get_font_path(script, size):
    font_options = font_map.get(script, font_map["english"])
    for font_path in font_options:
        try:
            font = get_font(font_path, size)
            return font_path
        except OSError:
            continue
    raise ValueError(f"No suitable font found for script: {script}")

def fits(font_size ,coord_width, coord_height, text, font_path, draw):
    try:
        font = get_font(font_path, font_size)
        text_bbox = draw.textbbox((0,0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        return (coord_width > text_width * 1.15 and
                coord_height > text_height * 1.15 and
                font_size >= 5)
    except Exception as e:
        print(f"Error with font size {font_size}: {e}")
        return False

def image_changer(filename, coordinates, words_to_print, current_time):
    image = cv2.imread(filename)
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    for coord in coordinates:
        x1, y1, x2, y2 = coord["x1"], coord["y1"], coord["x2"], coord["y2"]
        mask[y1:y2, x1:x2] = 255

    inpainted_image = cv2.inpaint(
        image, 
        mask, 
        inpaintRadius=3, 
        flags=cv2.INPAINT_NS  
    )

    inpainted_pil = Image.fromarray(cv2.cvtColor(inpainted_image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(inpainted_pil)

    texts = list(words_to_print.values())
    if len(texts) != len(coordinates):
        raise ValueError("number of texts and coordinates do not match")

    for coord, text in zip(coordinates, texts):
        text = normalize_text(text)
        x1, y1, x2, y2 = coord["x1"], coord["y1"], coord["x2"], coord["y2"]
        width = coord["width"]
        height = coord["height"] 

        script = detect_script(text)
        intial_font_size = 50
        font_path = get_font_path(script, intial_font_size)
        # Using binary search to find the optimal font size
        low = 5
        high = 500
        while low < high:
            mid = (low + high + 1) // 2
            if fits(mid, width, height, text, font_path, draw):
                low = mid
            else:
                high = mid - 1
        
        font_size = low if low <= 500 and fits(low, width, height, text, font_path, draw) else 5
        font = get_font(font_path, font_size)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]  # Calculate text width
        text_height = text_bbox[3] - text_bbox[1]
            
        x_center = x1 + (x2 - x1 - text_width) // 2
        y_center = y1 + (y2 - y1 - text_height) // 2
        draw.text((x_center, y_center), text, font=font, fill=(255, 0, 0))

    base_dir = r"./result"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    subfolder_path = os.path.join(base_dir, current_time)

    if not os.path.exists(subfolder_path):
        os.makedirs(subfolder_path)
    
    existing_files = [f for f in os.listdir(subfolder_path) if f.startswith("photo_")]
    if existing_files:
        existing_numbers = [int(f.split("_")[1].split(".")[0]) for f in existing_files]
        next_number = max(existing_numbers) + 1
    else:
        next_number = 1
    
    image_name = f"photo_{next_number}.pdf"
    output_path = os.path.join(subfolder_path, image_name)
    inpainted_pil.save(output_path)
    
