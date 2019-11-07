all:
	+$(MAKE) -C cencoder
	+$(MAKE) -C decoder

ifeq ($(OS),Windows_NT)

install:
	if not exist "bin" ( md "bin" )
	copy pyencoder\jpeg.py bin
	copy pyencoder\jpegTable.py bin
	copy pyencoder\lpy-jpeg-encoder.py bin
	copy cencoder\lpy-jpeg-encoder.exe bin
	copy decoder\lpy-jpeg-decoder.exe bin

uninstall:
	 rmdir /s /q bin

help:
	@echo install uninstall all

else

install:

	if [ ! -d "bin" ];then mkdir bin;	fi
	cp pyencoder/*.py cencoder/lpy-jpeg-encoder decoder/lpy-jpeg-decoder bin

uninstall:
	rm -rf bin

help:
	@echo install uninstall all

clean:
	+$(MAKE) -C cencoder clean
	+$(MAKE) -C decoder clean
endif