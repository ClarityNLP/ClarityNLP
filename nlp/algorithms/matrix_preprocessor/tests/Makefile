# locations of source files separated by ':'
#VPATH=../src

SRC = \
	test_preprocessor.cpp \
	main.cpp

# object files replace the .cpp extension with .o
OBJS = $(patsubst %.cpp, objs/%.o, $(SRC))

TARGET=test_preprocessor

# # paths to all include folders
INCLUDES = \
	-I../include

all: tests_bin

tests_bin: ../build/bin/$(TARGET)

# link the target binary
# bin/$(TARGET) : $(OBJS)
# 	@mkdir -p $(dir $@)
# 	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS) $(LIBS)

../build/bin/$(TARGET): $(OBJS)
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS) ../build/bin/$(LIBNAME).a $(LIBS)


# The -MMD switch causes several things to happen.  First, a makefile rule is
# generated that contains the the compiler to generate dependency files for 
# each file being compiled.  The dependency files are given a '.d' extension 
# and are written to the default location for preprocessed output.  The 
# 'include' statement below includes them in the makefile.  The -MP option 
# causes a phony target to be generated for each dependency other than the 
# main CPP file being compiled (such as for header files).  This feature 
# prevents the problem of having to include headers explicitly in the makefile
# and keeping them updated.
objs/%.o: %.cpp
	@mkdir -p $(dir $@)
	$(CXX) -c $(CXXFLAGS) $(INCLUDES) -MMD -MP -o $@ $<

clean:
	@rm -rf bin* objs*

# include all dependency files as individual targets
ifneq ($(MAKECMDGOALS),clean)
-include $(wildcard objs/*.d)
endif

.PHONY: clean all tests_bin

