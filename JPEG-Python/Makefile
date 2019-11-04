all:
	+$(MAKE) -C cencoder
	+$(MAKE) -C decoder

install:
	if [ ! -d "bin" ];then mkdir bin;	fi
	cp pyencoder/*.py cencoder/lpy_jpeg_encoder decoder/lpy-jpeg-decoder bin