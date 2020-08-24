import numpy as np
import os
import cv2


def TestGenetator(test_path, target_size=(256, 256)):
    for file_name in os.listdir(test_path):
       if file_name.split(".")[-1] in ["jpg", "jpeg", "png"]:
           print(file_name)
           image = cv2.imread(os.path.join(test_path, file_name), cv2.IMREAD_COLOR)
           image = cv2.resize(image, target_size[:2])
           image = image / 255
           image = np.reshape(image, (1,) + image.shape)
           yield image


def SaveImage(output_path, image_name, image):
    image = image[0] * 255
    cv2.imwrite(os.path.join(output_path, image_name), image)