from prometheus_client import Counter, Histogram
REQUEST_COUNT = Counter("http_requests_total","Count of HTTP requests",["method","endpoint","http_status"])
REQUEST_LATENCY = Histogram("http_request_latency_seconds","Latency of HTTP requests",["method","endpoint"])
INFERENCE_COUNT = Counter("denoise_inferences_total","Number of image denoise inferences",["model"])
INFERENCE_LATENCY = Histogram("denoise_inference_seconds","Latency for denoise inferences",["model"])
