from PIL import Image, ImageDraw
import numpy as np

def apply_eyelids(imgs: tuple[Image.Image, Image.Image], cfg: dict) -> tuple[Image.Image, Image.Image]:
    """
    Mask out each eyelid corner independently for both eyes.
    cfg must have keys:
      'eye1_top_left', 'eye1_top_right', 'eye1_bottom_left', 'eye1_bottom_right',
      'eye2_top_left', 'eye2_top_right', 'eye2_bottom_left', 'eye2_bottom_right'.
    Returns (left_eye_img, right_eye_img).
    """
    img1, img2 = imgs
    w, h = img1.size

    def make_mask(tl, tr, bl, br):
        m = Image.new("L", (w, h), 255)
        d = ImageDraw.Draw(m)
        # top lid
        d.polygon([(0,0),(w,0),(w, tr),(0, tl)], fill=0)
        # bottom lid
        d.polygon([(0,h),(w,h),(w, h - br),(0, h - bl)], fill=0)
        return m

    # build masks for each eye
    m1 = make_mask(cfg["eye1_top_left"], cfg["eye1_top_right"],
                   cfg["eye1_bottom_left"], cfg["eye1_bottom_right"])
    m2 = make_mask(cfg["eye2_top_left"], cfg["eye2_top_right"],
                   cfg["eye2_bottom_left"], cfg["eye2_bottom_right"])

    arr1 = np.array(img1)
    arr2 = np.array(img2)
    out1 = Image.fromarray(arr1 * (np.array(m1)[:, :, None] // 255))
    out2 = Image.fromarray(arr2 * (np.array(m2)[:, :, None] // 255))
    return out1, out2
