"""Darknet-53 for yolo v3.
   用keras搭建darknet53网络
"""
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, GlobalAveragePooling2D, Dense
from tensorflow.keras.layers import add, Activation, BatchNormalization
from tensorflow.keras.layers import LeakyReLU# .advanced_activations
from tensorflow.keras.regularizers import l2
from tensorflow.python.keras.layers.pooling import MaxPool2D, MaxPooling2D

def conv2d_unit(x, filters, kernels, strides=1):    #单纯的卷积
    """Convolution Unit
    This function defines a 2D convolution operation with BN and LeakyReLU.

    # Arguments
        x: Tensor, input tensor of conv layer.
        filters: Integer, the dimensionality of the output space.卷积核个数
        kernels: An integer or tuple/list of 2 integers, specifying the
            width and height of the 2D convolution window.
        strides: An integer or tuple/list of 2 integers,
            specifying the strides of the convolution along the width and
            height. Can be a single integer to specify the same value for
            all spatial dimensions.

    # Returns
            Output tensor.
    """
    x = Conv2D(filters, kernels,
               padding='same',
               strides=strides,
               activation='linear', #本身的激活函数为线性
               kernel_regularizer=l2(5e-4))(x)
    x = BatchNormalization()(x)
    x = LeakyReLU(alpha=0.1)(x)

    return x


def residual_block(inputs, filters):    #残差模块
    """Residual Block
    This function defines a 2D convolution operation with BN and LeakyReLU.

    # Arguments
        x: Tensor, input tensor of residual block.
        kernels: An integer or tuple/list of 2 integers, specifying the
            width and height of the 2D convolution window.卷积核大小

    # Returns
        Output tensor.
    """
    x = conv2d_unit(inputs, filters, (1, 1))
    x = conv2d_unit(x, 2 * filters, (3, 3)) #二倍关系
    x = add([inputs, x])    #合并
    x = Activation('linear')(x) #线性激活函数(并不做任何处理)

    return x


def stack_residual_block(inputs, filters, n):   #堆栈模块
    """Stacked residual Block
    """
    x = residual_block(inputs, filters) #残差模块

    for i in range(n - 1):
        x = residual_block(x, filters)  #堆起多层残差

    return x


def darknet_base(inputs):   #darknet基本结构
    """Darknet-53 base model.
    """

    x = conv2d_unit(inputs, 32, (3, 3))
    """
        后面开始卷积+多层残差(层数1，2，4，8)
    """
    x = conv2d_unit(x, 64, (3, 3), strides=2)
    x = stack_residual_block(x, 32, n=1)   

    x = conv2d_unit(x, 128, (3, 3), strides=2)
    x = stack_residual_block(x, 64, n=2)

    x = conv2d_unit(x, 256, (3, 3), strides=2)
    x = stack_residual_block(x, 128, n=8)

    x = conv2d_unit(x, 512, (3, 3), strides=2)
    x = stack_residual_block(x, 256, n=4)

    x = conv2d_unit(x, 1024, (3, 3), strides=2)
    x = stack_residual_block(x, 512, n=4)

    return x


def darknet():  #总的定义
    """Darknet-53 classifier.
    """
    inputs = Input(shape=(120, 120, 3))
    x = darknet_base(inputs)    #加载darknet基本结构

    x = GlobalAveragePooling2D()(x) #全局平均值池化
    x = Dense(11, activation='softmax')(x)    #全连接层

    model = Model(inputs, x)    #最终构成模型

    return model


# if __name__ == '__main__':
#     #定义模型并输出参数表
model = darknet()   
print(model.summary())
