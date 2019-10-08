CC = gcc
src = $(wildcard *.c)
obj = $(src:.c=.o)

app: $(obj)
	$(CC) -o $@ $^

run: app
	./app

.PHONY: clean
clean:
	rm -f $(obj) app
