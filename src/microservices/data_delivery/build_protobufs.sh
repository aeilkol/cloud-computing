#!/bin/sh

PROTOBUF_PATH=$1
python -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=. --grpc_python_out=. $PROTOBUF_PATH/data_delivery.proto
