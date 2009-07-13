.phony: all clean

progs = entropy pd_mkfile
all: $(progs)

GCC         ?= gcc
LD           = ld
CPP          = cpp
LIBS         = -lm
CFLAGS       = -Wall -Winline -O3 -ffast-math -Wdisabled-optimization
CFLAGS      += -g
DEFS         = -DPD_MKFILE_REPORT_RATE

%.o: %.c 
	$(GCC) $(CFLAGS) $(INC) $(DEFS) -c $< 

%.s: %.c
	$(GCC) $(CFLAGS) $(INC) $(DEFS) -S $< 

%.i: %.c
	$(GCC) $(CFLAGS) $(INC) $(DEFS) -E $< | indent -kr > $@

%: %.c
	$(GCC) $(LIBS) $(CFLAGS) $(INC) $(DEFS) -o $@ $<


clean:
	rm -f $(progs) *.o *.i *.s ;
