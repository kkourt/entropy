/*
 * Create a random file for a given probability distribution.
 * (too slow in python)
 *
 * The probability distribution will be given in stdin and must
 * be in the form of the following example:
 * --- cut here (start) ---
 *  .5
 *  .8
 *  .9
 *  .95
 *  .98
 *  1.0
 * ---- cut here (eof) ---
 *
 * Note that the the probabilities are sorted and accumulated
 * ( P(n) = p(n) + P(n-1) )
 *
 * number of probabilities must be <=256, so we can directly
 * map them to the char range.
 *
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <assert.h>
#include <time.h>

#define BUFFSIZE (4*1024*1024)
#define MIN(a,b) ((a<b) ? a:b)

#ifdef PD_MKFILE_REPORT_RATE
#include "timer.h"
#endif

/*
 * search for the output byte for a random number in [0,1).
 * we start from the end (most wide intervals) and go
 * all the way to the start. We could also do binary search
 * or a hybrid method
 */
unsigned char search(double *pds, int pds_len, double item)
{
	unsigned char i = (unsigned char)(pds_len-1);
	for (; i > 0; i--){
		if (pds[i] <= item){
			return  i;
		}
	}

	return 0;
}

int main(int argc, char **argv)
{
	double pds[256];
	unsigned long i;
	unsigned char buff[BUFFSIZE];

	srand48(time(NULL));

	if (argc < 3){
		fprintf(stderr, "Usage: %s <filename> <size>\n", argv[0]);
		exit(1);
	}

	char sbuff[1024];
	for (i=0;;){
		//printf("i=%lu\n", i);
		if ( fgets(sbuff, BUFFSIZE, stdin) == NULL ){
			break;
		}
		pds[i++] = strtod(sbuff, NULL);
	}
	assert(i <= 256);

	int pds_len = i;
	unsigned long fsize = atol(argv[2]);

	int fd = open(argv[1], O_CREAT | O_RDWR, S_IRUSR|S_IWUSR);
	if (fd == -1){
		perror("open");
		exit(1);
	}
	ftruncate(fd, fsize);

	unsigned long remaining = fsize;
	double rand;
	#ifdef PD_MKFILE_REPORT_RATE
	xtimer_t timer;
	timer_init(&timer);
	timer_start(&timer);
	#endif
	do {
		unsigned int s = MIN(BUFFSIZE, remaining);
		for (i=0; i < s; i++){
			rand = drand48();
			buff[i] = search(pds, pds_len, rand);
		}

		unsigned int written = 0;
		do {
			int ret = write(fd, buff, s);
			if (ret == -1){
				perror("write");
				exit(1);
			}
			written += ret;
		} while (s > written);

		remaining -= s;
		#ifdef PD_MKFILE_REPORT_RATE
		timer_pause(&timer);
		double secs = timer_secs(&timer);
		unsigned long bytes = (fsize - remaining);
		double Mbytes = ((double)bytes)/((double)(1024*1024));
		double rate = Mbytes/secs;
		printf("%lu (/%lu) in %lf secs [rate=%lf]\n", bytes, fsize, secs, rate);
		timer_start(&timer);
		#endif
	} while (remaining > 0);

	close(fd);
	return 0;
}
