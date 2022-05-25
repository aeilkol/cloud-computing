#!/bin/sh

PROTOBUF_PATH=protobufs

python3 -m grpc_tools.protoc -I protobufs --python_out=microservices/data_delivery --grpc_python_out=microservices/data_delivery $PROTOBUF_PATH/data_delivery.proto
python -m grpc_tools.protoc -I protobufs --python_out=microservices/data_delivery --grpc_python_out=microservices/data_delivery $PROTOBUF_PATH/logging.proto

python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=microservices/administrator_analysis --grpc_python_out=microservices/administrator_analysis $PROTOBUF_PATH/administrator_analysis.proto

python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=microservices/data_analysis --grpc_python_out=microservices/data_analysis $PROTOBUF_PATH/data_analysis.proto
python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=microservices/data_analysis --grpc_python_out=microservices/data_analysis $PROTOBUF_PATH/data_delivery.proto
python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=microservices/data_analysis --grpc_python_out=microservices/data_analysis $PROTOBUF_PATH/logging.proto

python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=microservices/logging --grpc_python_out=microservices/logging $PROTOBUF_PATH/logging.proto

python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=outbound --grpc_python_out=outbound $PROTOBUF_PATH/data_analysis.proto
python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=outbound --grpc_python_out=outbound $PROTOBUF_PATH/data_delivery.proto
python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=outbound --grpc_python_out=outbound $PROTOBUF_PATH/logging.proto
python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=outbound --grpc_python_out=outbound $PROTOBUF_PATH/administrator_analysis.proto
python3 -m grpc_tools.protoc -I $PROTOBUF_PATH --python_out=outbound --grpc_python_out=outbound $PROTOBUF_PATH/authentication.proto