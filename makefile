target = dist/pytetris.exe

all: $(target)

$(target): pytetris.py
	pyinstaller $< -w -F

test: all
	$(target)

clean:
	rm -rf build dist pytetris.spec
