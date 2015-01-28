PATH_TO_NANO_PB=/home/jtownley/Downloads/nanopb/generator
protoc --plugin=protoc-gen-nanopb=$PATH_TO_NANO_PB/protoc-gen-nanopb -I=src/resources/proto --nanopb_out=src/resources/due_protobuf_control src/resources/proto/messages.proto
