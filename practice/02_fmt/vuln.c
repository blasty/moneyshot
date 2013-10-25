#include <stdio.h>
#include <string.h>

void hello(char *name) {
	char buf[128];

	strncpy(buf, name, 127);
	buf[127] = 0;

	printf("Hello ");
	printf(buf);
	printf("!\n");
}


int main(int argc, char *argv[]) {
	if (argc != 2) {
		printf("Usage: %s <name>\n", argv[0]);
		return -1;
	}

	hello(argv[1]);

	return 0;
}
