import keras
import numpy as np
from model import *
from data_generator import *
from test import *
from keras.callbacks import ModelCheckpoint, LearningRateScheduler


def train():
    data_gen_args = dict(rotation_range=0.2,
                         width_shift_range=0.05,
                         height_shift_range=0.05,
                         shear_range=0.05,
                         zoom_range=0.05,
                         horizontal_flip=True,
                         fill_mode='nearest')
    myGene = trainGenerator(
        "./data", "image", "label",
        data_gen_args,
        (256, 256), (256,256),
        1,
        image_save_prefix="image",
        mask_save_prefix="mask",
        seed=1
    )
    model = unet('unet_membrane.hdf5')
    model_checkpoint = ModelCheckpoint('unet_membrane.hdf5', monitor='loss', verbose=1, save_best_only=True)
    # model.fit_generator(myGene, steps_per_epoch=5, epochs=10, callbacks=[model_checkpoint])

    testGene = TestGenetator("./data/test")
    results = model.predict_generator(testGene, 1, verbose=1)
    SaveImage("./data/res", "a.jpg", results)


if __name__ == '__main__':
    train()