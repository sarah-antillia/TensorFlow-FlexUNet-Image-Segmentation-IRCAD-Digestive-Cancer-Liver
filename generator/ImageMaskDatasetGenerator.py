# Copyright 2026 antillia.com Toshiyuki Arai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ImageMaskDatasetGenerator.py
# 2026/03/14

import os
import glob
import cv2
import shutil
import numpy as np
import nibabel as nib
import traceback

class ImageMaskDatasetGenerator:
  def __init__(self, size=512):
    pass
    self.file_format = ".png"
    self.RESIZE      = (512, 512)
  

  def  normalize(self, image):
    min1, max1 = image.min(), image.max()
    if max1 > min1:
      image = (image - min1) / (max1 - min1) * 255.0
    else:
      image = image * 0
    return image
  
  def colorize_mask(self, mask):
    h, w = mask.shape[:2]
    colorized = np.zeros((h, w, 3), dtype=np.uint8) 
    #You may change the following color.
    colorized[np.equal(mask,1)] = (40,40,180)  #bgr brown
    return colorized
  

  def generate(self, images_dir, masks_dir, output_images_dir, output_masks_dir): 
    index = 10000
  
    image_files = sorted(glob.glob(images_dir + "/*_orig.nii"))
    mask_files  = sorted(glob.glob(masks_dir  + "/*_liver.nii"))

    num_images = len(image_files)
    num_masks  = len(mask_files)
    num = min(num_images, num_masks)

    for i in range(num):
        index += 1
      
        idata  = nib.load(image_files[i])
        mdata  = nib.load(mask_files[i])
        images = idata.get_fdata()
        masks  = mdata.get_fdata()
        print(images.shape)
        print(masks.shape)

        h, w, n = images.shape
              
        for j in range(n):
          image = images[:,:,j] 
          mask  = masks[:,:,j]
          print(image.shape)
          if not (mask.any() >0):
            #Exclude empty masks.
            continue
          
          image = self.normalize(image)
           
          image = image.astype("uint8")
          image = cv2.resize(image, self.RESIZE)
          image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
          image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

          out_filename = str(index) + "_" + str(j+1) + ".png"
          out_imagefilepath = os.path.join(output_images_dir, out_filename )   
          cv2.imwrite(out_imagefilepath, image)
          print("Savd {}".format(out_imagefilepath))
        
          colorized = self.colorize_mask(mask)
          colorized = cv2.rotate(colorized, cv2.ROTATE_90_CLOCKWISE)
          colorized = cv2.resize(colorized, self.RESIZE)
          out_maskfilepath = os.path.join(output_masks_dir, out_filename )   

          cv2.imwrite(out_maskfilepath, colorized)
          print("Savd {}".format(out_maskfilepath))

 
if __name__ == "__main__":
  try:
    images_dir   = "./ircad-dataset/"   
    masks_dir    = "./ircad-dataset/"

    output_dir   = "./IRCAD-Digestive-Cancer"
    if os.path.exists(output_dir):
      shutil.rmtree(output_dir)
      os.makedirs(output_dir)
    
    output_images_dir = os.path.join(output_dir, "images")
    output_masks_dir  = os.path.join(output_dir, "masks")
  
    os.makedirs(output_images_dir)
    os.makedirs(output_masks_dir)
  
    generator = ImageMaskDatasetGenerator(size=512)
    generator.generate(images_dir,
                        masks_dir,
                        output_images_dir, 
                        output_masks_dir,)
  except:
    traceback.print_exc()