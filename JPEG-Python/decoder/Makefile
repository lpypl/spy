lpy-jpeg-decoder : decoder.o
	gcc -o $@ $^

decoder.o : decoder.c jpeg.h
	gcc -c $<

clean:
	rm decoder.o lpy-jpeg-decoder