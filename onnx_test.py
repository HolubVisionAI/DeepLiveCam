import onnxruntime as ort

# Path to your ONNX model
model_path = "./models/inswapper_128_fp16.onnx"

# Create session with TensorRT execution provider
providers = ['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']
try:
    sess = ort.InferenceSession(model_path, providers=providers)
    print("Execution Providers:", sess.get_providers())

    # Validate TensorRT usage
    if 'TensorrtExecutionProvider' in sess.get_providers():
        print("TensorRT Execution Provider is successfully enabled.")
    else:
        print("TensorRT Execution Provider is not available.")
except Exception as e:
    print(f"Error initializing the session: {e}")


import numpy as np

# Dummy input matching the ONNX model input shape
input_name = sess.get_inputs()[0].name
input_shape = sess.get_inputs()[0].shape
dummy_input = np.random.rand(*[dim if dim else 1 for dim in input_shape]).astype(np.float32)

# Run inference
outputs = sess.run(None, {input_name: dummy_input})
print("Inference ran successfully with TensorRT!")