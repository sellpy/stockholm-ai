"""Should export."""
import os
import tensorflow as tf
import keras.backend as K
import sys

from keras.models import load_model, Model, Sequential
from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import tag_constants
from tensorflow.python.saved_model.signature_def_utils_impl import (
    predict_signature_def)


def convert_keras_to_tf_model(model_name,
                              model_path="models/mnist_example",
                              sequential=True):
    """Convert keras model to tensorflow model."""
    # Needed to run multiple times in juptyter notebook.
    # TODO: figure out what is needed more.
    # Current solution: Start a separate process.
    sess = tf.Session()
    K.set_session(sess)

    # Because needed.
    K.set_learning_phase(0)

    # Load keras model

    path = model_path
    os.makedirs(path, exist_ok=True)
    loaded_model = load_model(model_name)

    config = loaded_model.get_config()
    weights = loaded_model.get_weights()
    if sequential:
        print("""Loading Sequential model,
                 specify sequential=False to load functional model""")
        new_model = Sequential.from_config(config)
        new_model.set_weights(weights)
    else:
        # Apparently different approach if Functional api.
        new_model = Model.from_config(config)

    # Check for storage location path
    if not os.path.exists(path):
        os.mkdir(path)
    version = 0
    versions = os.listdir(path)
    if len(versions) > 0:
        version = int(max(versions)) + 1
    export_path = os.path.join(
        tf.compat.as_bytes(path),
        tf.compat.as_bytes(str(version))
    )

    # Rebuild keras model to tensorflow serving format.
    builder = saved_model_builder.SavedModelBuilder(export_path)

    # Name inputs.
    input_dict = {}
    for idx, mod_input in enumerate(new_model.inputs):
        input_dict[
            "input_" + str(idx)
        ] = mod_input

    # Name outputs
    output_dict = {}
    for idx, mod_output in enumerate(new_model.outputs):
        output_dict[
            "output_" + str(idx)
        ] = mod_output

    signature = predict_signature_def(
        inputs=input_dict,
        outputs=output_dict
    )
    print(signature)
    with K.get_session() as sess:
        builder.add_meta_graph_and_variables(sess=sess,
                                             tags=[tag_constants.SERVING],
                                             signature_def_map={'predict':
                                                                signature})
        builder.save()

if __name__ == "__main__":
    print(sys.argv[1:])
    convert_keras_to_tf_model(*sys.argv[1:])
