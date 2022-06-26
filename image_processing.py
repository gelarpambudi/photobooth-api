import os
import cv2
import imageio
import numpy as np
from config import app
from PIL import Image
from scipy.interpolate import UnivariateSpline

from fimage import FImage
from fimage.filters import *
from fimage.presets import Preset



class BeautyFilter(Preset):
  filters = [
    Exposure(9),
    Brightness(1),
    Saturation(15),
    Contrast(4),
    Gamma(0.83),
    Vibrance(15)
  ]

class DarkenFilter(Preset):
  filters = [
    Contrast(8),
    Exposure(-5),
    Brightness(-10)
  ]

class LightenFilter(Preset):
  filters = [
    Exposure(0),
    Brightness(0),
    Contrast(0)
  ]


def load_cascade_classifier(classifier_path):
  return cv2.CascadeClassifier(classifier_path)

def load_image(img_path, transparent=False):
  if transparent:
    img = cv2.imread(img_path, -1)
  else:
    img = cv2.imread(img_path)
  return img


def save_image(np_img, save_path):
  cv2.imwrite(save_path, np_img)


def resize_image(np_img, new_size):
  image  = Image.fromarray(np_img)
  width  = image.size[0]
  height = image.size[1]

  aspect = width / float(height)

  ideal_width = new_size[0]
  ideal_height = new_size[1]
  ideal_aspect = ideal_width / float(ideal_height)

  if aspect > ideal_aspect:
      #crop the left and right edges:
      new_width = int(ideal_aspect * height)
      offset = (width - new_width) / 2
      resize = (offset, 0, width - offset, height)
  else:
      # crop the top and bottom:
      new_height = int(width / ideal_aspect)
      offset = (height - new_height) / 2
      resize = (0, offset, width, height - offset)

  result = image.crop(resize).resize((ideal_width, ideal_height), Image.ANTIALIAS)
  result = np.asarray(result)
  return result


def lookuptable(x, y):
  spline = UnivariateSpline(x,y)
  return spline(range(256))


def detect_face(img, cascade_classifier):
  grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  face_rects = cascade_classifier.detectMultiScale(grayscale, scaleFactor=1.1, minNeighbors=4)
  return face_rects


def apply_beauty_filter(img_path):
  img = FImage(img_path)
  img.apply(BeautyFilter)
  img.save(img_path)

  np_img = load_image(img_path)
  face = detect_face(
    np_img,
    load_cascade_classifier(app.config["CASCADE_CLASSIFIER_XML"])
  )
  
  for (x,y,w,h) in face:
    beauty = cv2.bilateralFilter(np_img[y:y+h, x:x+w], 7, 25, 25)
    np_img[y:y+h, x:x+w] = beauty

  return np_img


def apply_light_grayscale_effect(img_path):
  img = FImage(img_path)
  img.apply(LightenFilter)
  img.save(img_path)
  
  np_img = load_image(img_path)
  light_grayscale = cv2.cvtColor(np_img, cv2.COLOR_BGR2GRAY)
  return light_grayscale


def apply_dark_grayscale_effect(img_path):
  img = FImage(img_path)
  img.apply(DarkenFilter)
  img.save(img_path)
  
  np_img = load_image(img_path)
  dark_grayscale = cv2.cvtColor(np_img, cv2.COLOR_BGR2GRAY)
  return dark_grayscale


def apply_sepia_effect(np_img):
  sepia = np.array(np_img, dtype=np.float64)
  sepia = cv2.transform(sepia, np.matrix([[0.272, 0.534, 0.131],
                                  [0.349, 0.686, 0.168],
                                  [0.393, 0.769, 0.189]]))
  sepia[np.where(sepia > 255)] = 255
  sepia = np.array(sepia, dtype=np.uint8)
  return sepia


def apply_summer_effect(np_img):
  increaseLookupTable = lookuptable([0, 64, 128, 256], [0, 80, 160, 256])
  decreaseLookupTable = lookuptable([0, 64, 128, 256], [0, 50, 100, 256])
  blue_channel, green_channel, red_channel  = cv2.split(np_img)
  red_channel = cv2.LUT(red_channel, increaseLookupTable).astype(np.uint8)
  blue_channel = cv2.LUT(blue_channel, decreaseLookupTable).astype(np.uint8)
  summer= cv2.merge((blue_channel, green_channel, red_channel))
  return summer


def apply_winter_effect(np_img):
  increaseLookupTable = lookuptable([0, 64, 128, 256], [0, 80, 160, 256])
  decreaseLookupTable = lookuptable([0, 64, 128, 256], [0, 50, 100, 256])
  blue_channel, green_channel,red_channel = cv2.split(np_img)
  red_channel = cv2.LUT(red_channel, decreaseLookupTable).astype(np.uint8)
  blue_channel = cv2.LUT(blue_channel, increaseLookupTable).astype(np.uint8)
  winter = cv2.merge((blue_channel, green_channel, red_channel))
  return winter


def apply_hdr_effect(np_img):
    hdr = cv2.detailEnhance(np_img, sigma_s=12, sigma_r=0.15)
    return hdr


def apply_invert_effect(np_img):
    inv = cv2.bitwise_not(np_img)
    return inv


def apply_all_effect(img_np, result_path, image):
    img_file = image

    #save original effect
    if "original" in app.config['AVAILABLE_EFFECT']:
      save_image(img_np, os.path.join(result_path, f"original/{img_file}"))
      beauty_img = apply_beauty_filter(os.path.join(result_path, f"original/{img_file}"))
      save_image(beauty_img, os.path.join(result_path, f"original/{img_file}"))
    
    #apply and save light grayscale
    if "light_grayscale" in app.config['AVAILABLE_EFFECT']:
      save_image(img_np, os.path.join(result_path, f"light_grayscale/{img_file}"))
      light_grayscale_img = apply_light_grayscale_effect(os.path.join(result_path, f"original/{img_file}"))
      save_image(light_grayscale_img, os.path.join(result_path, f"light_grayscale/{img_file}"))

    #apply and save dark grayscale
    if "dark_grayscale" in app.config['AVAILABLE_EFFECT']:
      save_image(img_np, os.path.join(result_path, f"dark_grayscale/{img_file}"))
      dark_grayscale_img = apply_dark_grayscale_effect(os.path.join(result_path, f"original/{img_file}"))
      save_image(dark_grayscale_img, os.path.join(result_path, f"dark_grayscale/{img_file}"))

    #apply and save summer
    if "summer" in app.config['AVAILABLE_EFFECT']:
      summer_img = apply_summer_effect(img_np)
      save_image(summer_img, os.path.join(result_path, f"summer/{img_file}"))


def generate_gif(img_path, out_gif, delay=1.5):
  img_files = os.listdir(img_path)
  if "compiled.jpg" in img_files:
    img_files.remove("compiled.jpg")
  with imageio.get_writer(out_gif, mode='I', duration=delay) as writer:
    for filename in img_files:
        image = imageio.imread(os.path.join(img_path, filename))
        writer.append_data(image)


def compile_np_image(img_path, img_list, padding=30, new_size=(560,480), mirror=True):
  max_width = 0
  total_height = 0
  images = []

  for img_file in img_list:
    img_full_path = os.path.join(img_path, img_file)
    img=load_image(img_full_path)
    img=resize_image(img, new_size)
    images.append(img)

    image_width=img.shape[1]
    image_height=img.shape[0]
    if image_width > max_width:
        max_width = image_width
    total_height += image_height

  final_image = np.zeros((total_height+(len(img_list)-1)*padding,max_width,3),dtype=np.uint8)
  current_y = 0

  for image in images:
    height = image.shape[0]
    width = image.shape[1]
    final_image[current_y:height+current_y,:width,:] = image
    current_y += height + padding
  return final_image


def overlay_transparent(bg_img, img_to_overlay_t):
    b,g,r,a = cv2.split(img_to_overlay_t)
    overlay_color = cv2.merge((b,g,r))
    mask = cv2.medianBlur(a,5)

    img1_bg = cv2.bitwise_and(bg_img.copy(),bg_img.copy(),mask = cv2.bitwise_not(mask))
    img2_fg = cv2.bitwise_and(overlay_color,overlay_color,mask = mask)
    bg_img = cv2.add(img1_bg, img2_fg)

    return bg_img


def create_padding(padding_width=None, padding_height=None):
  padding = np.zeros([padding_height,padding_width,3], dtype=np.uint8)
  return padding


def compile_frame(frame_id, src_img_path, frame_base_dir):
  frame_name = f"frame-{frame_id}.png"
  frame_img = load_image(os.path.join(frame_base_dir, frame_name), True)
  img_list = os.listdir(src_img_path)  

  if frame_name in app.config['AVAILABLE_6_FRAME']:
    compiled_image = compile_np_image(
      src_img_path,
      img_list,
      padding=94,
      new_size=(993,945) #(width, height)
    )
    center_padding = create_padding(
      padding_width=188,
      padding_height=compiled_image.shape[0]
    )
    
    compiled_image = cv2.hconcat([compiled_image, center_padding, compiled_image])

    height_diff = frame_img.shape[0] - compiled_image.shape[0]
    top_padding = create_padding(
      padding_width=compiled_image.shape[1],
      padding_height=83
    )
    bottom_padding = create_padding(
      padding_width=compiled_image.shape[1],
      padding_height= height_diff - top_padding.shape[0]
    )

    compiled_image = cv2.vconcat([top_padding, compiled_image, bottom_padding])
    
    width_diff = frame_img.shape[1] - compiled_image.shape[1]
    right_padding = create_padding(
      padding_width=width_diff//2,
      padding_height=compiled_image.shape[0]
    )
    left_padding = create_padding(
      padding_width=(width_diff//2)+1,
      padding_height= compiled_image.shape[0]
    )

    compiled_image = cv2.hconcat([left_padding, compiled_image, right_padding])
    final_image = overlay_transparent(compiled_image, frame_img)

    return final_image
  elif frame_name in app.config['AVAILABLE_6_FRAME_6_TAKES']:
    compiled_col_1 = compile_np_image(
      src_img_path,
      img_list[3:],
      padding=94,
      new_size=(993,945) #(width, height)
    )
    compiled_col_2 = compile_np_image(
      src_img_path,
      img_list[:3],
      padding=94,
      new_size=(993,945) #(width, height)
    )
    center_padding = create_padding(
      padding_width=188,
      padding_height=compiled_col_2.shape[0]
    )
    
    compiled_image = cv2.hconcat([compiled_col_1, center_padding, compiled_col_2])

    height_diff = frame_img.shape[0] - compiled_image.shape[0]
    top_padding = create_padding(
      padding_width=compiled_image.shape[1],
      padding_height=83
    )
    bottom_padding = create_padding(
      padding_width=compiled_image.shape[1],
      padding_height= height_diff - top_padding.shape[0]
    )

    compiled_image = cv2.vconcat([top_padding, compiled_image, bottom_padding])
    
    width_diff = frame_img.shape[1] - compiled_image.shape[1]
    right_padding = create_padding(
      padding_width=width_diff//2,
      padding_height=compiled_image.shape[0]
    )
    left_padding = create_padding(
      padding_width=(width_diff//2)+1,
      padding_height= compiled_image.shape[0]
    )

    compiled_image = cv2.hconcat([left_padding, compiled_image, right_padding])
    final_image = overlay_transparent(compiled_image, frame_img)

    return final_image
    
  elif frame_name in app.config['AVAILABLE_8_FRAME'] and frame_name not in app.config['AVAILABLE_8_FRAME_ELLIPSE']:
    compiled_image_col = compile_np_image(
      src_img_path,
      img_list,
      padding=22,
      new_size=(992,781)
    )
    center_padding = create_padding(
      padding_width=188,
      padding_height=compiled_image_col.shape[0]
    )

    compiled_image = cv2.hconcat([compiled_image_col, center_padding, compiled_image_col])
    
    height_diff = frame_img.shape[0] - compiled_image.shape[0]
    top_padding = create_padding(
      padding_width=compiled_image.shape[1],
      padding_height=71
    )
    bottom_padding = create_padding(
      padding_width=compiled_image.shape[1],
      padding_height= height_diff - top_padding.shape[0]
    )

    compiled_image = cv2.vconcat([top_padding, compiled_image, bottom_padding])

    width_diff = frame_img.shape[1] - compiled_image.shape[1]
    right_padding = create_padding(
      padding_width=width_diff//2,
      padding_height=compiled_image.shape[0]
    )
    left_padding = create_padding(
      padding_width=(width_diff//2)+1,
      padding_height= compiled_image.shape[0]
    )

    compiled_image = cv2.hconcat([left_padding, compiled_image, right_padding])
    final_image = overlay_transparent(compiled_image, frame_img)

    return final_image

  elif frame_name in app.config['AVAILABLE_8_FRAME'] and frame_name in app.config['AVAILABLE_8_FRAME_ELLIPSE']:
    compiled_image_col = compile_np_image(
      src_img_path,
      img_list,
      padding=87,
      new_size=(1022,716)
    )
    center_padding = create_padding(
      padding_width=158,
      padding_height=compiled_image_col.shape[0]
    )

    compiled_image = cv2.hconcat([compiled_image_col, center_padding, compiled_image_col])
    
    height_diff = frame_img.shape[0] - compiled_image.shape[0]
    top_padding = create_padding(
      padding_width=compiled_image.shape[1],
      padding_height=172
    )
    bottom_padding = create_padding(
      padding_width=compiled_image.shape[1],
      padding_height= height_diff - top_padding.shape[0]
    )

    compiled_image = cv2.vconcat([top_padding, compiled_image, bottom_padding])

    width_diff = frame_img.shape[1] - compiled_image.shape[1]
    right_padding = create_padding(
      padding_width=width_diff//2,
      padding_height=compiled_image.shape[0]
    )
    left_padding = create_padding(
      padding_width=(width_diff//2)+1,
      padding_height= compiled_image.shape[0]
    )

    compiled_image = cv2.hconcat([left_padding, compiled_image, right_padding])
    final_image = overlay_transparent(compiled_image, frame_img)

    return final_image