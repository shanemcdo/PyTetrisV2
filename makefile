target = dist/pytetris.exe

all: $(target)

$(target): pytetris.py
	pyinstaller $< --onefile --noconsole --clean

test: all
	$(target)

clean:
	rm -rf build dist pytetris.spec
