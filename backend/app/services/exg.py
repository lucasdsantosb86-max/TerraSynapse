import numpy as np
def compute_exg(img_rgb: np.ndarray):
    img = img_rgb.astype("float32") / 255.0
    R, G, B = img[...,0], img[...,1], img[...,2]
    exg = 2*G - R - B
    exg_mean = float(exg.mean())
    return exg, exg_mean
