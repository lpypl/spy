ifeq ($(OS),Windows_NT)
	TARGET = lpy-jpeg-encoder.exe
else
	TARGET = lpy-jpeg-encoder
endif

$(TARGET) : main.o jpeg.o jpeg-binary-tools.o
	gcc -o $@ $^

jpeg.o : jpeg.c jpeg.h
	gcc -c $<

jpeg-binary-tools.o : jpeg-binary-tools.c jpeg-binary-tools.h
	gcc -c $<

main.o :  main.c jpeg.h jpeg-binary-tools.h
	gcc -c $<

ifeq ($(OS),Windows_NT)

clean:
	del *.o 
	del *.exe

else

clean:
	rm -rf lpy-jpeg-decoder *.o

endif