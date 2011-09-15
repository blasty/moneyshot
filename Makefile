all: win32 linux

win32:
	i586-mingw32msvc-gcc -o test_sc_win32.exe test_sc_win32.c	

linux:
	gcc -o test_sc test_sc.c
