# Makefile for C++ sparse matrix preprocessor library and test program.

# locations of source code files, each path separated by ':'
VPATH=src

# detect the operating system
# returns either 'Darwin' (MacOSX) or 'Linux'
UNAME := $(shell uname)

# Linux needs to explicitly link with librt
SYSTEM_FILE := system_mac.cpp
ifeq ($(UNAME), Linux)
LIBRT := -lrt
SYSTEM_FILE := system_posix.cpp
endif

# macros passed directly to the compiler on the command line
DEFINES :=

# compiler flags, linker flags, and libs for all configurations
CXXFLAGS += $(DEFINES) -Wall -std=c++11 -O2
LDFLAGS += -v 
LIBS = $(LIBRT) -lm

# source files for the library
LIB_SRC = \
	constants.cpp                 \
	error.cpp                     \
	matrix_market_file.cpp        \
	preprocess.cpp                \
	spooky_v2.cpp                 \
	system_mac.cpp                \
	system_posix.cpp              \
	term_frequency_matrix.cpp     \
	utils.cpp                     \
	score.cpp                     \
	term_occurrence_histogram.cpp

# source files for the C++ preprocessor application
PREPROCESSOR_SRC = \
	command_line.cpp \
	main.cpp

# object files replace the .cpp extension with .o
LIB_OBJS  = $(patsubst %.cpp, build/objs/%.o, $(LIB_SRC))
PREPROCESSOR_OBJS = $(patsubst %.cpp, build/objs/%.o, $(PREPROCESSOR_SRC))

# paths to all include folders
INCLUDES = \
	-Iinclude

# name of lib binary
LIB_TARGET=libpreprocess
LIBNAME=$(LIB_TARGET)

export CXX
export CXXFLAGS
export LDFLAGS
export LIBS
export LIBNAME

# name of test program binary
PREPROCESSOR_TARGET=preprocessor

all: libpreprocess tests preprocessor  #tester

libpreprocess: build/bin/$(LIBNAME).a

#tester: libpreprocess build/bin/$(PREPROCESSOR_TARGET)

preprocessor: libpreprocess build/bin/$(PREPROCESSOR_TARGET)

tests: libpreprocess
	cd tests && $(MAKE) all

build/objs/%.o: %.cpp
	@mkdir -p $(dir $@)
	$(CXX) -c $(CXXFLAGS) $(INCLUDES) -MMD -MP -o $@ $<

build/bin/$(LIBNAME).a : $(LIB_OBJS)
	@mkdir -p $(dir $@)
	ar rs build/bin/$(LIBNAME).a $(LIB_OBJS)

build/bin/$(PREPROCESSOR_TARGET): $(PREPROCESSOR_OBJS)
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS) build/bin/$(LIBNAME).a $(LIBS)

clean:
	@rm -rf build bin* objs* *~
	cd tests && $(MAKE) clean

.PHONY: all clean libpreprocess tests #tester
