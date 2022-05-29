import os
import cv2
import imageio
import numpy as np
from config import app
from scipy.interpolate import UnivariateSpline

def load_image(img_path, transparent=False):
  if transparent:
    img = cv2.imread(img_path, -1)
  else:
    img = cv2.imread(img_path)
  return img

def save_image(np_img, save_path):
  cv2.imwrite(save_path, np_img)

def resize_image(np_img, new_size):
  return cv2.resize(np_img, new_size, cv2.INTER_AREA)

def lookuptable(x, y):
  spline = UnivariateSpline(x,y)
  return spline(range(256))


def apply_grasycale_effect(np_img):
  grayscale = cv2.cvtColor(np_img, cv2.COLOR_BGR2GRAY)
  return grayscale


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
    save_image(img_np, os.path.join(result_path, f"original/{img_file}"))
    
    #apply and save grayscale
    grayscale_img = apply_grasycale_effect(img_np)
    save_image(grayscale_img, os.path.join(result_path, f"grayscale/{img_file}"))

    #apply and save sepia
    sepia_img = apply_sepia_effect(img_np)
    save_image(sepia_img, os.path.join(result_path, f"sepia/{img_file}"))

    #apply and save summer
    summer_img = apply_summer_effect(img_np)
    save_image(summer_img, os.path.join(result_path, f"summer/{img_file}"))

    #apply and save winter
    winter_img = apply_winter_effect(img_np)
    save_image(winter_img, os.path.join(result_path, f"winter/{img_file}"))

    #apply and save hdr
    hdr_img = apply_hdr_effect(img_np)
    save_image(hdr_img, os.path.join(result_path, f"hdr/{img_file}"))

    #apply and save invert
    invert_img = apply_invert_effect(img_np)
    save_image(invert_img, os.path.join(result_path, f"invert/{img_file}"))


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
      padding=70,
      new_size=(1100,980) #(width, height)
    )
    center_padding = create_padding(
      padding_width=65,
      padding_height=compiled_image.shape[0]
    )
    
    compiled_image = cv2.hconcat([compiled_image, center_padding, compiled_image])

    height_diff = frame_img.shape[0] - compiled_image.shape[0]
    top_padding = create_padding(
      padding_width=compiled_image.shape[1],
      padding_height=60
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
      padding_width=width_diff//2,
      padding_height= compiled_image.shape[0]
    )

    compiled_image = cv2.hconcat([left_padding, compiled_image, right_padding])
    final_image = overlay_transparent(compiled_image, frame_img)

    return final_image
  elif frame_name in app.config['AVAILABLE_8_FRAME'] and frame_name not in app.config['AVAILABLE_8_FRAME_ELLIPSE']:
    compiled_image_1 = compile_np_image(
      src_img_path,
      img_list[:4],
      padding=20,
      new_size=(1150,790)
    )
    compiled_image_2 = compile_np_image(
      src_img_path,
      img_list[4:],
      padding=20,
      new_size=(1150,790)
    )
    center_padding = create_padding(
      padding_width=30,
      padding_height=compiled_image_1.shape[0]
    )

    compiled_image = cv2.hconcat([compiled_image_1, center_padding, compiled_image_2])
    
    height_diff = frame_img.shape[0] - compiled_image.shape[0]
    top_padding = create_padding(
      padding_width=compiled_image.shape[1],
      padding_height=30
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
    compiled_image_1 = compile_np_image(
      src_img_path,
      img_list[:4],
      padding=20,
      new_size=(1130,790)
    )
    compiled_image_2 = compile_np_image(
      src_img_path,
      img_list[4:],
      padding=20,
      new_size=(1130,790)
    )
    center_padding = create_padding(
      padding_width=70,
      padding_height=compiled_image_1.shape[0]
    )

    compiled_image = cv2.hconcat([compiled_image_1, center_padding, compiled_image_2])
    
    height_diff = frame_img.shape[0] - compiled_image.shape[0]
    top_padding = create_padding(
      padding_width=compiled_image.shape[1],
      padding_height=130
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