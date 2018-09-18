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

#include <cstdio>
#include <string>
#include <cstring>
#include <cstdlib>
#include <unistd.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>

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
