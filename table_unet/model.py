from keras.layers import Conv2D, MaxPool2D, Dropout, concatenate, UpSampling2D, Input
from keras.models import Model
from keras.optimizers import Adam


def unet(pretrain_weight=None, inputs=(256, 256, 3)):
    input = Input(inputs)

    conv1 = Conv2D(64, 3, padding='same', kernel_initializer='he_normal', activation='relu')(input)
    conv1 = Conv2D(64, 3, padding='same', kernel_initializer='he_normal', activation='relu')(conv1)
    pool1 = MaxPool2D(pool_size=(2, 2))(conv1)
    # output: 128*128*64

    conv2 = Conv2D(128, 3, padding='same', kernel_initializer='he_normal', activation='relu')(pool1)
    conv2 = Conv2D(128, 3, padding='same', kernel_initializer='he_normal', activation='relu')(conv2)
    pool2 = MaxPool2D(pool_size=(2, 2))(conv2)
    # output: 64*64*128

    conv3 = Conv2D(256, 3, padding='same', kernel_initializer='he_normal', activation='relu')(pool2)
    conv3 = Conv2D(256, 3, padding='same', kernel_initializer='he_normal', activation='relu')(conv3)
    pool3 = MaxPool2D(pool_size=(2, 2))(conv3)
    # output:32*32*256

    conv4 = Conv2D(512, 3, padding='same', kernel_initializer='he_normal', activation='relu')(pool3)
    conv4 = Conv2D(512, 3, padding='same', kernel_initializer='he_normal', activation='relu')(conv4)
    drop4 = Dropout(0.5)(conv4)
    pool4 = MaxPool2D(pool_size=(2, 2))(drop4)
    # output:16*16*512

    conv5 = Conv2D(1024, 3, padding='same', kernel_initializer='he_normal', activation='relu')(pool4)
    conv5 = Conv2D(1024, 3, padding='same', kernel_initializer='he_normal', activation='relu')(conv5)
    drop5 = Dropout(0.5)(conv5)
    # output 8*8*1024

    upsample6 = UpSampling2D(size=(2, 2))(drop5)
    up6 = Conv2D(512, 2, padding='same', kernel_initializer='he_normal', activation='relu')(upsample6)
    merge6 = concatenate([conv4, up6], axis=3)
    conv6 = Conv2D(512, 3, padding='same', kernel_initializer='he_normal', activation='relu')(merge6)
    conv6 = Conv2D(512, 3, padding='same', kernel_initializer='he_normal', activation='relu')(conv6)

    upsample7 = UpSampling2D(size=(2, 2))(conv6)
    up7 = Conv2D(256, 2, padding='same', kernel_initializer='he_normal', activation='relu')(upsample7)
    merge7 = concatenate([conv3, up7], axis=3)
    conv7 = Conv2D(256, 3, padding='same', kernel_initializer='he_normal', activation='relu')(merge7)
    conv7 = Conv2D(256, 3, padding='same', kernel_initializer='he_normal', activation='relu')(conv7)

    upsample8 = UpSampling2D(size=(2,2))(conv7)
    up8 = Conv2D(128, 2, padding='same', kernel_initializer='he_normal', activation='relu')(upsample8)
    merge8 = concatenate([conv2, up8], axis=3)
    conv8 = Conv2D(128, 3, padding='same', kernel_initializer='he_normal', activation='relu')(merge8)
    conv8 = Conv2D(128, 3, padding='same', kernel_initializer='he_normal', activation='relu')(conv8)

    upsample9 = UpSampling2D(size=(2, 2))(conv8)
    up9 = Conv2D(64, 2, padding='same', kernel_initializer='he_normal', activation='relu')(upsample9)
    merge9 = concatenate([conv1, up9], axis=3)
    conv9 = Conv2D(64, 3, padding='same', kernel_initializer='he_normal', activation='relu')(merge9)
    conv9 = Conv2D(64, 3, padding='same', kernel_initializer='he_normal', activation='relu')(conv9)

    conv10 = Conv2D(2, 3, padding='same', kernel_initializer='he_normal', activation='relu')(conv9)
    conv10 = Conv2D(1, 1, activation='sigmoid')(conv10)

    model = Model(inputs=input, outputs=conv10)
    model.compile(optimizer=Adam(lr=1e-4), loss='binary_crossentropy', metrics=['accuracy'])

    model.summary()
    if pretrain_weight:
        model.load_weights(pretrain_weight)

    return model