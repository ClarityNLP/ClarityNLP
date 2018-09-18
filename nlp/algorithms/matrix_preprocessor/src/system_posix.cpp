// Copyright 2014 Georgia Institute of Technology
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <string>
#include <cstdint>
#include <stdlib.h>
//#include "timer.hpp"
//#include <time.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>

// #define MEGA (1000000ull)
// #define GIGA (1000ull * MEGA)

// //----------------------------------------------------------------------------
// Timer::Timer() : tStart_(0), tStop_(0), freq_Hz_(0)

// {
// 	struct timespec ts;

// 	if(clock_getres(CLOCK_REALTIME,&ts)){
// 		throw "Couldn't get realtime clock resolution";
// 	}
// 	freq_Hz_ = GIGA / (ts.tv_nsec + ts.tv_sec * GIGA);
// }

// //----------------------------------------------------------------------------
// void Timer::Start()
// {
// 	struct timespec ts;

// 	if(clock_gettime(CLOCK_REALTIME,&ts)){
// 		throw "Couldn't read realtime clock";
// 	}
// 	tStart_ = ts.tv_nsec + ts.tv_sec * GIGA;
// }

// //----------------------------------------------------------------------------
// void Timer::Stop()
// {
// 	struct timespec ts;

// 	if(clock_gettime(CLOCK_REALTIME,&ts)){
// 		throw "Couldn't read realtime clock";
// 	}
// 	tStop_ = ts.tv_nsec + ts.tv_sec * GIGA;
// }

// //----------------------------------------------------------------------------
// int64_t Timer::ReportNanoseconds()
// {
//     return GIGA * (tStop_ - tStart_) / freq_Hz_;
// }

// //----------------------------------------------------------------------------
// int64_t Timer::ReportMicroseconds()
// {
//     return MEGA * (tStop_ - tStart_) / freq_Hz_;
// }

// //----------------------------------------------------------------------------
// int64_t Timer::ReportMilliseconds()
// {
//     if (tStop_ < tStart_)
//         return 0;
//     else
//         return 1000 * (tStop_ - tStart_) / freq_Hz_;
// }

// //----------------------------------------------------------------------------
// int64_t Timer::ReportSeconds()
// {
//     return (tStop_ - tStart_) / freq_Hz_;
// }

//----------------------------------------------------------------------------
bool DirectoryExists(const std::string& dir)
{
    struct stat st;
    if (0 == stat(dir.c_str(), &st))
    {
        return (S_IFDIR == (st.st_mode & S_IFDIR));
    }

    return false;
}

//----------------------------------------------------------------------------
bool GetCurrentDirectory(std::string& dir)
{
    char* buf = 0;
    char* curdir = getcwd(buf, 0);
    if (NULL == curdir)
    {
        dir = strerror(errno);
        return false;
    }

    dir = std::string(curdir);
    free(curdir);
    return true;
}

//----------------------------------------------------------------------------
bool SetCurrentDirectory(std::string& dir)
{
    int result = chdir(dir.c_str());
    if (0 != result)
    {
        dir = strerror(errno);
        return false;
    }

    return true;
}
