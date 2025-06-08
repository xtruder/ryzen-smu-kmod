.PHONY: build clean

download:
	spectool  -g -C . ryzen-smu-kmod.spec

build: download
	fedpkg --release f42 mockbuild

clean:
	-rm -rf results_ryzen-smu-kmod
	-rm -rf ryzen-smu-kmod-*.tar.gz
	-rm -rf ryzen-smu-kmod-*.rpm
