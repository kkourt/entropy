.phony: all clean

progs = entropy pd_mkfile
all: $(progs)

CPU         ?= $(shell $(shell rsrc resource cpu_info.sh))
MHZ         ?= $(shell $(shell rsrc resource cpu_mhz.sh))

GCC         ?= gcc
#GCC         = icc
LD           = ld
CPP          = cpp
LIBS         = -lm
CFLAGS       = -Wall -Winline -O3 -ffast-math -Wdisabled-optimization
CFLAGS      += -g
DEFS         = -DCPU_$(CPU) -DCPU_MHZ=$(MHZ) -DPD_MKFILE_REPORT_RATE
INC          = -I$(shell rsrc resource 'prfcnt')

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
