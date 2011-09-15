#include <stdio.h>
#include <sys/mman.h>
#include <string.h>
#include <stdlib.h>
#include "shellcode.h"

int (*sc)();

int main(int argc, char **argv) {
    void *ptr = mmap(0, sizeof(shellcode),
            PROT_EXEC | PROT_WRITE | PROT_READ, MAP_ANON
            | MAP_PRIVATE, -1, 0);
 
    if (ptr == MAP_FAILED) {
        perror("mmap");
        exit(-1);
    }
 
    memcpy(ptr, shellcode, sizeof(shellcode));
    sc = ptr;
 
    sc();
 
    return 0;
}
