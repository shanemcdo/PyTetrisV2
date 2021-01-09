target = dist/pytetris.exe

all: $(target)

$(target): pytetris.py *.py
	pyinstaller $< -w -F

zip: all
	cp $(target) .
	tar -acf release.zip pytetris.exe assets
	rm pytetris.exe
	
release: zip clean

test: all
	$(target)

clean:
	rm -rf build dist pytetris.spec
