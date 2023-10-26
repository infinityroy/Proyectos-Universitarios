# solo usar make server -B

BIN=downloadex

all: $(BIN)

server: DNS_interceptor.c
	gcc -g -Wall DNS_interceptor.c -o DNS_interceptor.o -ljson-c -lpthread -lm -l curl -lb64
	./DNS_interceptor.o
