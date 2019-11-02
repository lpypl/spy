app : jpeg.o constructJPEG.o
	gcc -o $@ $^

jpeg.o : jpeg.c jpeg.h
	gcc -c $<

constructJPEG.o : constructJPEG.c jpeg.h
	gcc -c $<