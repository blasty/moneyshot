#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "shellcode.h"

int (*sc)();

int main(int argc, char **argv) {
    sc = shellcode;
 
    sc();
 
    return 0;
}
