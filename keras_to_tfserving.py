"""Should export."""
import os
import tensorflow as tf
import keras.backend as K

from keras.models import load_model, Model, Sequential
from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import tag_constants
from tensorflow.python.saved_model.signature_def_utils_impl import (
    predict_signature_def)

# Because needed.
K.set_learning_phase(0)

# Load keras model

path = 'models/mnist_example'
os.makedirs(path, exist_ok=True)
loaded_model = load_model("mnist_example.m")

config = loaded_model.get_config()
weights = loaded_model.get_weights()
# Apparently different approach if Functional api.
# new_model = Model.from_config(config)

# Apparently different approach if Sequential api.
new_model = Sequential.from_config(config)
new_model.set_weights(weights)


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
