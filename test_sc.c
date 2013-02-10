#include <stdio.h>
#include <sys/mman.h>
#include <string.h>
#include <stdlib.h>

int (*sc)();

int main(int argc, char **argv) {
	FILE *f;

    void *ptr = mmap(0, 8192,
            PROT_EXEC | PROT_WRITE | PROT_READ, MAP_ANON
            | MAP_PRIVATE, -1, 0);
 
    if (ptr == MAP_FAILED) {
        perror("mmap");
        exit(-1);
    }

	f = fopen(argv[1], "rb");
	fread(ptr, 8192, 1, f);
	fclose(f);

    sc = ptr;
 
    sc();
 
    return 0;
}
