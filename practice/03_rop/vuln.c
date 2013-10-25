#include <stdio.h>
#include <string.h>

void readinput(char *dst) {
	read(0, dst, 127);
}

void hello(char *name) {
	char buf[256];
	char msg[128];

	strcpy(buf, name);

	printf("enter a message: ");
	fflush(stdout);
	readinput(msg);

	printf("OK, bye.\n");
}

void main(int argc, char *argv[]) {
	if (argc != 2) {
		printf("Usage: %s <name>\n", argv[0]);
		return -1;
	}

	printf("You are: ");
	system("whoami");

	hello(argv[1]);

	exit(0);
}
