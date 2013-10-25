#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define PORT_NO 9191
#define MAXMSG 256

int make_socket (uint16_t port) {
	int sock;
	int yes = 1;
	struct sockaddr_in name;

	/* Create the socket. */
	sock = socket (PF_INET, SOCK_STREAM, 0);
	if (sock < 0) {
		perror ("socket");
		exit (EXIT_FAILURE);
	}

	/* Give the socket a name. */
	name.sin_family = AF_INET;
	name.sin_port = htons (port);
	name.sin_addr.s_addr = htonl (INADDR_ANY);

	if ( setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int)) == -1 ) {
		perror("setsockopt");
	}

	if (bind (sock, (struct sockaddr *) &name, sizeof (name)) < 0) {
		perror ("bind");
		exit (EXIT_FAILURE);
	}

	return sock;
}

int handle_client(int fd) {
	char buffer[MAXMSG];
	int nbytes=0;

	unsigned char welcome_msg[]="> Damn Vulnerable Daemon v0.2\n";
	unsigned char ack_msg[]="> Thank you for your message!\n";

	write(fd, welcome_msg, strlen(welcome_msg));

	nbytes = read (fd, buffer, MAXMSG*2);
	write(fd, ack_msg, strlen(ack_msg));
	close(fd);

	return 0;
}

int main(int argc, char *argv[]) {
	int i;
	int sock, connfd;
	struct sockaddr_in clientname;
	size_t size;
	pid_t     childpid;

	FILE *fi;

	/* Create the socket and set it up to accept connections. */
	sock = make_socket (PORT_NO);
	if (listen (sock, 1) < 0) {
		perror ("listen");
		exit (EXIT_FAILURE);
	}

	for(;;) {
		size = sizeof (clientname);
		connfd = accept(sock, (struct sockaddr *) &clientname, &size);

		if (connfd == -1) {
			sleep(1);
			continue;
		}

		printf("++ CLIENT CONNECTED! FD = %d\n", connfd);

		if ((childpid = fork()) == 0) {
			handle_client(connfd);

			close (sock);

		}

		close(connfd);
	}

	return 0;
}
