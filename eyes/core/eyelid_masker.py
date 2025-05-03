from PIL import Image, ImageDraw
import numpy as np

def apply_eyelids(img: Image.Image, cfg: dict) -> Image.Image:
    """
    Mask out each eyelid corner independently. 
    cfg must have keys: top_left, top_right, bottom_left, bottom_right.
    """
    w, h = img.size
    mask = Image.new("L", (w, h), 255)  # start fully visible
    draw = ImageDraw.Draw(mask)

    # Top lid: trapezoid from y=0 down to max(top_left, top_right)
    tl = cfg["top_left"]
    tr = cfg["top_right"]
    draw.polygon([(0,0), (w,0), (w, tr), (0, tl)], fill=0)

    # Bottom lid: trapezoid from y=h down to h - max(bottom_left, bottom_right)
    bl = cfg["bottom_left"]
    br = cfg["bottom_right"]
    draw.polygon([
        (0, h), (w, h), 
        (w, h - br), (0, h - bl)
    ], fill=0)

    # Combine mask with original image
    arr = np.array(img)
    m  = np.array(mask)[:, :, None]  # H×W×1
    # wherever mask==0, zero out pixels
    arr = arr * (m // 255)
    return Image.fromarray(arr)