"""Send image to tensorflow serving.

Hint: the code has been compiled together with TensorFlow serving
and not locally. The client is called in the TensorFlow Docker container
"""

from __future__ import print_function

# Communication to TensorFlow server via gRPC
# from grpc.beta import implementations
import tensorflow as tf

# TensorFlow serving stuff to send messages
# from tensorflow_serving.apis import predict_pb2
# from tensorflow_serving.apis import prediction_service_pb2

import os
import requests

import cv2

import numpy as np

import sys

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2

import logging
import grpc

from grpc import RpcError
from flask import Flask, jsonify, request
from flask_cors import CORS
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
CORS(app)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.info('flask app initialized')


def create_gprc_client(host):
    """Simple wrapper."""
    channel = grpc.insecure_channel(host)
    stub = prediction_service_pb2.PredictionServiceStub(channel)
    request = predict_pb2.PredictRequest()
    return stub, request


class PredictClientClassification():
    """Prediction Client."""

    def __init__(self, host, model_name, model_version=0):
        """I."""
        # super().__init__(host, model_name, model_version)
        self.host = host
        self.model_name = model_name
        self.model_version = model_version

    def predict():
        """Needed for abstract method."""
        return True

    def predict_mnist(self, request_data, request_timeout=10):
        """Predict."""
        # Create gRPC client and request
        stub, request = create_gprc_client(self.host)
        request.model_spec.name = self.model_name
        request.model_spec.signature_name = "predict"
        # if self.model_version > 0:
        #     request.model_spec.version.value = self.model_version

        features_tensor_proto = tf.contrib.util.make_tensor_proto(
            request_data, dtype=tf.float32, shape=request_data.shape)
        request.inputs['input_0'].CopyFrom(features_tensor_proto)

        try:
            result = stub.Predict(request, timeout=request_timeout)
            return list(result.outputs['output_0'].float_val)
        except RpcError as e:
            print("hej", e)


@app.route('/')
def ok():
    """Standard Return."""
    return ('ok:')


@app.route('/health_check')
def health_check():
    """Health Check."""
    return 'healthy'


@app.route('/predict/image_position', methods=['POST'])
def predict_image_position():
    """Post req."""
    prediction_request = request.get_json()
    url = prediction_request["url"]

    r = requests.get(url)
    nparr = np.frombuffer(r.content, np.uint8)
    img = cv2.imdecode(nparr, 0)
    img = cv2.resize(img, (28, 28))
    img = (np.expand_dims(img, 0) / 255.).astype(np.float32)
    # Grayscale image so add channel last.
    img = np.expand_dims(img, 3)
    print(img.shape)
    mnist_client = PredictClientClassification(
        "serve_tensorflow:9000", "mnist_example_model")

    output = mnist_client.predict_mnist(img)
    output_class = dict(zip(list(range(0, 10)), list(output)))

    return jsonify(
        output_classification=output_class)


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8080
    print("serving!")
    WSGIServer((host, port), app, log=None).serve_forever()
