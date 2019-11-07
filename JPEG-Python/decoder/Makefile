ifeq ($(OS),Windows_NT)
	TARGET = lpy-jpeg-decoder.exe
else
	TARGET = lpy-jpeg-decoder
endif

$(TARGET) : decoder.o main.o util.o
	g++ -o $@ $^

decoder.o : decoder.cpp jpeg.h
	g++ -c $<

main.o : main.cpp decoder.h
	g++ -c $<

util.o : util.cpp util.h
	g++ -c $<

clean:
	rm -rf lpy-jpeg-decoder *.o *.exe