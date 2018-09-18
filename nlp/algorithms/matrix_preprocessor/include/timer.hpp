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

#pragma once

#include <chrono>

//----------------------------------------------------------------------------
class Timer
{
public:

    Timer() {}

    void Start() {start_ = std::chrono::high_resolution_clock::now();}
    void Stop()  {stop_  = std::chrono::high_resolution_clock::now();}

    uint64_t ReportMicroseconds() 
    {return std::chrono::duration_cast<std::chrono::microseconds>(stop_-start_).count();}
    uint64_t ReportMilliseconds()
    {return std::chrono::duration_cast<std::chrono::milliseconds>(stop_-start_).count();}
    uint64_t ReportSeconds()
    {return std::chrono::duration_cast<std::chrono::seconds>(stop_-start_).count();}

private:

    std::chrono::high_resolution_clock::time_point start_;
    std::chrono::high_resolution_clock::time_point stop_;
};

