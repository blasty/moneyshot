all: win32 linux

win32:
	i586-mingw32msvc-gcc -o test_sc_win32.exe test_sc_win32.c	

linux:
	gcc -m32 -o test_sc_lnx_x86 test_sc.c
	gcc -m64 -o test_sc_lnx_x86_64 test_sc.c
