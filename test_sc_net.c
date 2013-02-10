#include <stdio.h>
#include <netinet/in.h>
#include <netdb.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <signal.h>

int (*sc)();

static void error(char *msg) {
	perror(msg);
	exit(1);
}

static void SIGCHLD_Handler(int sig) {
	waitpid(-1, NULL, WNOHANG);
}

int main(int argc, char *argv[]) {
	int sockfd, newsockfd, portno, clilen;
	struct sockaddr_in serv_addr, cli_addr;
	struct sigaction sigact;

	sigact.sa_handler = SIGCHLD_Handler;
	if (sigaction(SIGCHLD, &sigact, 0)) error("sighandle def");

	if (argc < 2) {
		fprintf(stderr,"ERROR, no port provided\n");
		exit(1);
	}
 
	void *ptr = mmap(0, 8192, PROT_EXEC | PROT_WRITE | PROT_READ, MAP_ANON | MAP_PRIVATE, -1, 0);
	printf("Mapped exec page @ %p\n", ptr);
	if (ptr == MAP_FAILED) {
		perror("mmap");
		exit(-1);
	}

	sockfd = socket(AF_INET, SOCK_STREAM, 0);

	if (sockfd < 0) error("ERROR opening socket");
	bzero((char *) &serv_addr, sizeof(serv_addr));
	portno = atoi(argv[1]);
	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = INADDR_ANY;
	serv_addr.sin_port = htons(portno);
	if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) error("ERROR on binding");
	listen(sockfd,5);
	clilen = sizeof(cli_addr);
	printf("server online.\n");

	while (1) {
		newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
		if (newsockfd < 0)
			error("ERROR on accept");

		if(read(newsockfd, ptr, 256) > 0) {		
			sc = ptr;
			printf("launching SC.. hold BREATH!!\n");
			sc();
		}
	}

	return 0;
}
