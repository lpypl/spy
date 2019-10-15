hdr = $(wildcard *.h)
src = $(wildcard *.c)
obj = $(src:.c=.o)

main : $(obj) 
	gcc $^ -o $@ 

%.o : %.c $(hdr)
	gcc -c $<

clean:
	rm *.o main

