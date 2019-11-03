lpy-jpeg-decoder : decoder.o main.o
	g++ -o $@ $^

decoder.o : decoder.cpp jpeg.h
	g++ -c $<

main.o : main.cpp decoder.h
	g++ -c $<

clean:
	rm decoder.o lpy-jpeg-decoder main.o