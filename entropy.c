/*
 * entropy.c:
 * measure the entropy of a file, using bytes as symbols
 * Kornilios Kourtis <kkourt@cslab.ece.ntua.gr>
 */
#define _GNU_SOURCE

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MIN(a,b) ((a<b)?a:b)

#define BUFFSIZE 4096
int main(int argc, char **argv)
{
	char *fname;
	unsigned long offset, size, cnt, ret;
	int fd, i;
	unsigned long symbols[256];
	unsigned char buff[BUFFSIZE];
	double entropy;

	if (argc < 2){
		fprintf(stderr,"Usage: %s filename <offset> <size>\n", argv[0]);
		exit(1);
	}
	fname = argv[1];

	offset = (argc>2) ? atol(argv[2]) : 0;
	size = (argc>3) ? atol(argv[3]) : ~0;

	for(i=0; i<256; i++) symbols[i] = 0;
	
	fd = open(fname, O_RDONLY);
	if (fd == -1){
		perror("open");
		exit(1);
	}

	ret = lseek(fd, offset, SEEK_SET);
	if ( ret == (off_t)-1){
		perror("lseek");
		exit(1);
	}

	cnt = 0;
	do {
		ret = read(fd, buff, MIN(size, BUFFSIZE));
		if (!ret) break;
		cnt += ret;

		for (i=0; i<ret; i++) symbols[buff[i]]++;

	} while  (cnt < size);

	entropy = 0;
	for(i=0; i<256; i++){
		if (symbols[i]){
			double p = ((double)symbols[i]/(double)cnt);
			entropy -= p*log2(p);
		}
	}

	printf("entropy for %s <%lu->%lu>: %3.2lf\n", fname, offset, cnt, entropy);
	return 0;
}
