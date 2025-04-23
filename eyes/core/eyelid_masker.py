from PIL import Image
import numpy as np

def apply_eyelids(img, eyelid_config):
    arr = np.array(img)
    if eyelid_config.get('top', 0) > 0:
        arr[:eyelid_config['top'], :, :] = 0
    if eyelid_config.get('bottom', 0) > 0:
        arr[-eyelid_config['bottom']:, :, :] = 0
    if eyelid_config.get('left', 0) > 0:
        arr[:, :eyelid_config['left'], :] = 0
    if eyelid_config.get('right', 0) > 0:
        arr[:, -eyelid_config['right']:, :] = 0
    return Image.fromarray(arr)
