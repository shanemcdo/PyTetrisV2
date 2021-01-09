target = dist/pytetris.exe

all: $(target)

$(target): pytetris.py *.py
	pyinstaller $< -w -F

release: all
	cp -r assets dist
	Explorer dist

test: all
	$(target)

clean:
	rm -rf build dist pytetris.spec
