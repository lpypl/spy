all:
	+$(MAKE) -C cencoder
	+$(MAKE) -C decoder

install:
	if [ ! -d "bin" ];then mkdir bin;	fi
	cp pyencoder/*.py cencoder/lpy-jpeg-encoder decoder/lpy-jpeg-decoder bin

uninstall:
	rm -rf bin

help:
	@echo help install uninstall all