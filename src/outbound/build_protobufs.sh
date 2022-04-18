#!/bin/sh

PROTOBUF_PATH=$1
python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=. --grpc_python_out=. $PROTOBUF_PATH/data_analysis.proto
python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=. --grpc_python_out=. $PROTOBUF_PATH/data_delivery.proto
python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=. --grpc_python_out=. $PROTOBUF_PATH/logging.proto
python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=. --grpc_python_out=. $PROTOBUF_PATH/administrator_analysis.proto
python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=. --grpc_python_out=. $PROTOBUF_PATH/authentication.proto
