from __future__ import print_function
from keras.models import Sequential
from keras.layers.core import Dense
from keras.layers.core import Reshape
from keras.layers import Merge
from keras.layers.core import Activation
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.normalization import BatchNormalization
from keras.layers.convolutional import ZeroPadding3D
from keras.layers.convolutional import Convolution2D, Convolution3D

#创造中间卷积层，这是中间用于抽取空间特性的部分， 定义了一个四层的纯卷积层的卷积神经网络，最后得到卷积的结果作为输出
def seqCNN(n_flow=4, seq_len=3, map_height=32, map_width=32):
    model = Sequential()
    model.add(Convolution2D(64, 3, 3, input_shape=(n_flow*seq_len, map_height, map_width), border_mode='same'))
    model.add(Activation('relu'))

    model.add(Convolution2D(128, 3, 3, border_mode='same'))
    model.add(Activation('relu'))

    model.add(Convolution2D(64, 3, 3, border_mode='same'))
    model.add(Activation('relu'))

    model.add(Convolution2D(n_flow, 3, 3, border_mode='same'))
    model.add(Activation('tanh'))
    return model

def seqCNNBase(conf=(4, 3, 32, 32)):
    n_flow, seq_len, map_height, map_width = conf
    #
    model = Sequential()
    model.add(Convolution2D(64, 3, 3, input_shape=(n_flow*seq_len, map_height, map_width), border_mode='same'))
    model.add(Activation('relu'))

    model.add(Convolution2D(128, 3, 3, border_mode='same'))
    model.add(Activation('relu'))

    model.add(Convolution2D(64, 3, 3, border_mode='same'))
    model.add(Activation('relu'))

    model.add(Convolution2D(n_flow, 3, 3, border_mode='same'))
    # model.add(Activation('tanh'))
    return model


def seqCNNBaseLayer1(conf=(4, 3, 32, 32)):
    # 1 layer CNN for early fusion     这是最简单的就一层的cnn结构，用于早期融合使用
    n_flow, seq_len, map_height, map_width = conf
    model = Sequential()
    model.add(Convolution2D(64, 3, 3, input_shape=(n_flow * seq_len, map_height, map_width), border_mode='same'))
    model.add(Activation('relu'))
    return model


def seqCNN_CPT(c_conf=(4, 3, 32, 32), p_conf=(4, 3, 32, 32), t_conf=(4, 3, 32, 32)):
    '''
    C - Temporal Closeness
    P - Period
    T - Trend
    conf = (nb_flow, seq_len, map_height, map_width)
    '''
    model = Sequential()
    components = []
    #这是针对时空数据 时间性三个特点的融合方法，   会将经过卷积处理过的时间数据  再卷积以下来融合到一起
    for conf in [c_conf, p_conf, t_conf]:
        if conf is not None:
            components.append(seqCNNBaseLayer1(conf))
            nb_flow = conf[0]
    model.add(Merge(components, mode='concat', concat_axis=1))  # concat
    model.add(Convolution2D(64, 3, 3, border_mode='same'))
    model.add(Activation('relu'))

    model.add(Convolution2D(64, 3, 3, border_mode='same'))
    model.add(Activation('relu'))

    model.add(Convolution2D(nb_flow, 3, 3, border_mode='same'))
    model.add(Activation('tanh'))
    return model


def seqCNNBaseLayer1_2(conf=(4, 3, 32, 32)):
    # 1 layer CNN for early fusion   另一个单层用于早期融合的单卷积层
    n_flow, seq_len, map_height, map_width = conf
    model = Sequential()
    model.add(Convolution2D(64, 3, 3, input_shape=(n_flow * seq_len, map_height, map_width), border_mode='same'))
    # model.add(Activation('relu'))
    return model


def seqCNN_CPT2(c_conf=(4, 3, 32, 32), p_conf=(4, 3, 32, 32), t_conf=(4, 3, 32, 32)):
    '''
    C - Temporal Closeness
    P - Period
    T - Trend
    conf = (nb_flow, seq_len, map_height, map_width)
    针对时空数据时间性的第二种融合方式，加入卷积层的结构
    '''
    model = Sequential()
    components = []

    for conf in [c_conf, p_conf, t_conf]:
        if conf is not None:
            components.append(seqCNNBaseLayer1_2(conf))
            nb_flow = conf[0]
    # model.add(Merge(components, mode='concat', concat_axis=1))  # concat
    if len(components) > 1:
        model.add(Merge(components, mode='sum'))
    else:
        model = components[0]
    model.add(Activation('relu'))
    model.add(Convolution2D(64, 3, 3, border_mode='same'))
    model.add(Activation('relu'))

    model.add(Convolution2D(64, 3, 3, border_mode='same'))
    model.add(Activation('relu'))

    model.add(Convolution2D(nb_flow, 3, 3, border_mode='same'))
    model.add(Activation('tanh'))
    return model


def seqCNN_CPTM(c_conf=(4, 3, 32, 32), p_conf=(4, 3, 32, 32), t_conf=(4, 3, 32, 32), metadata_dim=None):
    '''
    C - Temporal Closeness
    P - Period
    T - Trend
    conf = (nb_flow, seq_len, map_height, map_width)
    metadata_dim
    加入卷积层之后  加上全连接层，。
    '''
    model = Sequential()
    components = []
    for conf in [c_conf, p_conf, t_conf]:
        if conf is not None:
            components.append(seqCNNBaseLayer1_2(conf))
            # nb_flow = conf[0]
            nb_flow, _, map_height, map_width = conf
    # model.add(Merge(components, mode='concat', concat_axis=1))  # concat
    if len(components) > 1:
        model.add(Merge(components, mode='sum'))
    else:
        model = components[0]
    model.add(Activation('relu'))
    model.add(Convolution2D(64, 3, 3, border_mode='same'))
    model.add(Activation('relu'))

    model.add(Convolution2D(64, 3, 3, border_mode='same'))
    model.add(Activation('relu'))

    model.add(Convolution2D(nb_flow, 3, 3, border_mode='same'))

    metadata_processor = Sequential()
    # metadata_processor.add(Dense(output_dim=nb_flow * map_height * map_width, input_dim=metadata_dim))
    metadata_processor.add(Dense(output_dim=10, input_dim=metadata_dim))
    metadata_processor.add(Activation('relu'))
    metadata_processor.add(Dense(output_dim=nb_flow * map_height * map_width))
    metadata_processor.add(Activation('relu'))
    metadata_processor.add(Reshape((nb_flow, map_height, map_width)))

    model_final=Sequential()
    model_final.add(Merge([model, metadata_processor], mode='sum'))
    model_final.add(Activation('tanh'))
    return model_final


def lateFusion(metadata_dim, n_flow=2, seq_len=3, map_height=32, map_width=32):
    model=Sequential()
    mat_model=seqCNNBase(n_flow, seq_len, map_height, map_width)
    metadata_processor=Sequential()
    metadata_processor.add(Dense(output_dim=n_flow * map_height * map_width, input_dim=metadata_dim))
    metadata_processor.add(Reshape((n_flow, map_height, map_width)))
    # metadata_processor.add(Activation('relu'))

    model=Sequential()
    model.add(Merge([mat_model, metadata_processor], mode='sum'))
    model.add(Activation('tanh'))
    return model


def seqCNN_BN(n_flow=4, seq_len=3, map_height=32, map_width=32):
    model=Sequential()
    model.add(Convolution2D(64, 3, 3, input_shape=(n_flow*seq_len, map_height, map_width), border_mode='same'))
    model.add(LeakyReLU(0.2))
    model.add(BatchNormalization())

    model.add(Convolution2D(128, 3, 3, border_mode='same'))
    model.add(LeakyReLU(0.2))
    model.add(BatchNormalization())

    model.add(Convolution2D(64, 3, 3, border_mode='same'))
    model.add(LeakyReLU(0.2))
    model.add(BatchNormalization())

    model.add(Convolution2D(n_flow, 3, 3, border_mode='same'))
    model.add(Activation('tanh'))
    return model


def seqCNN_LReLU(n_flow=4, seq_len=3, map_height=32, map_width=32):
    model=Sequential()
    model.add(Convolution2D(64, 3, 3, input_shape=(n_flow*seq_len, map_height, map_width), border_mode='same'))
    model.add(LeakyReLU(0.2))
    # model.add(BatchNormalization())

    model.add(Convolution2D(128, 3, 3, border_mode='same'))
    model.add(LeakyReLU(0.2))
    # model.add(BatchNormalization())

    model.add(Convolution2D(64, 3, 3, border_mode='same'))
    model.add(LeakyReLU(0.2))
    # model.add(BatchNormalization())

    model.add(Convolution2D(n_flow, 3, 3, border_mode='same'))
    model.add(Activation('tanh'))
    return model


def seq3DCNN(n_flow=4, seq_len=3, map_height=32, map_width=32):
    model=Sequential()
    # model.add(ZeroPadding3D(padding=(0, 1, 1), input_shape=(n_flow, seq_len, map_height, map_width)))
    # model.add(Convolution3D(64, 2, 3, 3, border_mode='valid'))
    model.add(Convolution3D(64, 2, 3, 3, border_mode='same', input_shape=(n_flow, seq_len, map_height, map_width)))
    model.add(Activation('relu'))

    model.add(Convolution3D(128, 2, 3, 3, border_mode='same'))
    model.add(Activation('relu'))

    model.add(Convolution3D(64, 2, 3, 3, border_mode='same'))
    model.add(Activation('relu'))

    model.add(ZeroPadding3D(padding=(0, 1, 1)))
    model.add(Convolution3D(n_flow, seq_len, 3, 3, border_mode='valid'))
    # model.add(Convolution3D(n_flow, seq_len-2, 3, 3, border_mode='same'))
    model.add(Activation('tanh'))
    return model