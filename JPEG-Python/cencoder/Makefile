lpy-jpeg-encoder : main.o jpeg.o jpeg-binary-tools.o
	gcc -o $@ $^

jpeg.o : jpeg.c jpeg.h
	gcc -c $<

jpeg-binary-tools.o : jpeg-binary-tools.c jpeg-binary-tools.h
	gcc -c $<

main.o :  main.c jpeg.h jpeg-binary-tools.h
	gcc -c $<

clean :
	rm main.o jpeg.o jpeg-binary-tools.o lpy_jpeg_encoder