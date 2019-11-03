lpy-jpeg-decoder : decoder.o
	g++ -o $@ $^

decoder.o : decoder.cpp jpeg.h
	g++ -c $<

clean:
	rm decoder.o lpy-jpeg-decoder