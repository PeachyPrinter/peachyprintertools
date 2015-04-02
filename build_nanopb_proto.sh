PATH_TO_NANO_PB=/opt/git/nanopb/generator
protoc --plugin=protoc-gen-nanopb=$PATH_TO_NANO_PB/protoc-gen-nanopb -I=src/resources/proto --nanopb_out=src/resources/due_protobuf_control src/resources/proto/messages.proto
