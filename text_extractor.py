# from PIL import Image, ImageDraw, ImageFont
# import numpy as np

# def replace_text(image_path, coordinates, new_text="Mihir Desai", text_color=(255, 0, 0)):
#     # Open image
#     img = Image.open(image_path)
#     draw = ImageDraw.Draw(img)
    
#     # Extract coordinates
#     x1, y1, x2, y2 = coordinates[0]["x1"], coordinates[0]["y1"], coordinates[0]["x2"], coordinates[0]["y2"]
    
#     # Get background color by sampling the area around text
#     border_pixels = []
#     for x in range(x1-2, x2+3):
#         border_pixels.extend([img.getpixel((x, y1-2)), img.getpixel((x, y2+2))])
#     for y in range(y1-2, y2+3):
#         border_pixels.extend([img.getpixel((x1-2, y)), img.getpixel((x2+2, y))])
    
#     bg_color = tuple(int(np.median([p[i] for p in border_pixels])) for i in range(3))
    
#     # Remove old text by filling with background color
#     draw.rectangle([x1, y1, x2, y2], fill=bg_color)
    
#     # Find optimal font size
#     font_size = 20
#     while font_size > 5:
#         try:
#             font = ImageFont.truetype("arial.ttf", font_size)
#         except OSError:
#             font = ImageFont.load_default()
#             break
            
#         bbox = draw.textbbox((0, 0), new_text, font=font)
#         text_width = bbox[2] - bbox[0]
#         text_height = bbox[3] - bbox[1]
        
#         if text_width <= (x2 - x1):
#             break
#         font_size -= 1
    
#     # Center and draw new text
#     x_center = x1 + ((x2 - x1) - text_width) // 2
#     y_center = y1 + ((y2 - y1) - text_height) // 2
#     draw.text((x_center, y_center), new_text, font=font, fill=text_color)
    
#     img.save("output.jpg")
#     return img

from PIL import ImageFont

def is_font_present(font_path):
    try:
        ImageFont.truetype(font_path, size=12)  # Any size will do
        return True
    except OSError:
        return False

# Test for Noto Sans Devanagari
font_path = "NotoSansDevanagari-Regular.ttf"
if is_font_present(font_path):
    print(f"'{font_path}' is present.")
else:
    print(f"'{font_path}' is not found.")