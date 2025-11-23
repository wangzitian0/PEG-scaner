# This file makes 'generated' a Python package and exposes helpers for proto imports.
import sys

from . import stock_pb2 as stock_pb2

# Protoc emits absolute imports (e.g., `import stock_pb2`) even when the files live
# inside this package. Register the module so `import stock_pb2` resolves correctly.
sys.modules.setdefault('stock_pb2', stock_pb2)
