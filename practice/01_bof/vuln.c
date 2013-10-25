#include <stdio.h>
#include <string.h>

void hello(char *name) {
	char buf[256];

	sprintf(buf, "Hello there, %s", name);

	printf("%s\n", buf);
}


int main(int argc, char *argv[]) {
	if (argc != 2) {
		printf("Usage: %s <name>\n", argv[0]);
		return -1;
	}

	hello(argv[1]);

	return 0;
}
