#! coding: utf8
import keras.backend as K
from keras.layers import Lambda, merge
from keras.models import Model

import tensorflow as tf


class Parallelizer(object):
    def __init__(self):
        self.n_gpus = self._get_n_gpus()

    def _get_n_gpus(self):
        """Get numbers of available GPUs."""
        from tensorflow.python.client import device_lib
        return len([
            1
            for x in device_lib.list_local_devices()
            if x.device_type == 'GPU'
        ])

    def transform(self, model):
        def get_slice(data, idx, parts):
            is_last_slice = idx == parts - 1
            
            shape = K.shape(data)
            minibatch_size, features = shape[:1], shape[1:]
            stride = K.concatenate([minibatch_size//parts, features*0], axis=0)
            if is_last_slice:
                # feed everything else if it's the last slice
                size = K.concatenate([[-1], features], axis=0)
            else:
                size = K.concatenate([minibatch_size//parts, features], axis=0)
            begin = stride * idx
            return tf.slice(data, begin, size)

        outputs_all = [[] for i in model.outputs]

        # Place a copy of the model on each GPU
        # each getting a slice of the batch
        for gpu_id in xrange(self.n_gpus):
            with tf.device('/gpu:%d' % gpu_id):
                with tf.name_scope('tower_%d' % gpu_id) as scope:
                    inputs = []
                    # Slice each input into a piece for processing on this GPU
                    for x in model.inputs:
                        input_shape = tuple(x.get_shape().as_list())[1:]
                        slice_n = Lambda(
                            get_slice,
                            output_shape=input_shape,
                            arguments={
                                'idx': gpu_id,
                                'parts': self.n_gpus
                            })(x)
                        inputs.append(slice_n)

                    outputs = model(inputs)

                    if not isinstance(outputs, list):
                        outputs = [outputs]

                    # Save all the outputs for merging back together later
                    for l in xrange(len(outputs)):
                        outputs_all[l].append(outputs[l])

        # all output tensors on CPU
        with tf.device('/cpu:0'):
            return Model(
                inputs=model.inputs,
                outputs=[
                    # merge outputs from all GPU
                    concatenate(o, axis=0)
                    for o in outputs_all
                ]
            )
