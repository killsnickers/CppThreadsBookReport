from keras.preprocessing.image import ImageDataGenerator
import numpy as np


def trainGenerator(
        data_path, image_folder, mask_folder,
        aug_dict,
        imag_target_size, mask_target_size,
        batch_size,
        image_save_prefix="image",
        mask_save_prefix="mask",
        seed=1
    ):
    image_data_generator = ImageDataGenerator(**aug_dict)
    mask_data_generator = ImageDataGenerator(**aug_dict)
    image_generator = image_data_generator.flow_from_directory(
        data_path,
        target_size=imag_target_size,
        classes=[image_folder],
        color_mode="rgb",
        class_mode=None,
        batch_size=batch_size,
        save_to_dir=None,
        save_prefix=image_save_prefix,
        seed=seed
    )
    mask_generator = mask_data_generator.flow_from_directory(
        data_path,
        target_size=mask_target_size,
        classes=[mask_folder],
        color_mode="grayscale",
        class_mode=None,
        batch_size=batch_size,
        save_to_dir=None,
        save_prefix=mask_save_prefix,
        seed=seed
    )
    train_genetator = zip(image_generator, mask_generator)
    for (image, mask) in train_genetator:
        image = image_prehandle(image)
        mask = mask_prehandle(mask)
        yield (image, mask)


def image_prehandle(image):
    image = image / 255
    return image


def mask_prehandle(mask):
    mask = mask / 255
    mask[mask > 0.5] = 1
    mask[mask <= 0.5] = 0
    return mask

