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

#include <cctype>
#include <string>
#include <fstream>
#include <iostream>
#include <algorithm>
#include <stdexcept>
#include "utils.hpp"
#include "constants.hpp"

//-----------------------------------------------------------------------------
void ToUpper(std::string& str)
{
    for (auto &c : str)
        c = toupper(c);
}

//-----------------------------------------------------------------------------
void ToLower(std::string& str)
{
    for (auto &c : str)
        c = tolower(c);
}

//-----------------------------------------------------------------------------
std::string TrimQuotes(const std::string& str)
{
    static const char SINGLE_QUOTE = '\'';
    static const char DOUBLE_QUOTE = '\"';

    size_t l=0, r=str.size()-1;

    for (; l != str.size(); ++l)
        if ( (SINGLE_QUOTE != str[l]) && (DOUBLE_QUOTE != str[l]))
            break;

    for (; r != 0; --r)
        if ( (SINGLE_QUOTE != str[r]) && (DOUBLE_QUOTE != str[r]))
            break;

    return str.substr(l, r-l+1);
}

//-----------------------------------------------------------------------------
std::string EnsureTrailingPathSep(const std::string& str)
{
    static const char PATH_SEP = '/';

    // ignore if empty string
    if (str.empty())
        return std::string("");
    
    size_t sz = str.size();
    if (PATH_SEP == str[sz-1])
        return str;
    else
        return (str + PATH_SEP);
}

//-----------------------------------------------------------------------------
std::string FileExtension(const std::string& filename)
{
    std::string ext;  // empty string

    // look for the final '.' character
    auto dot_pos = filename.rfind('.');
    if (std::string::npos != dot_pos)
    {
        ext = filename.substr(dot_pos + 1);
        ToUpper(ext);
    }

    return ext;
}

//-----------------------------------------------------------------------------
std::string TrimExtension(const std::string& filename)
{
    std::string result(filename);

    // look for the final '.' character
    auto dot_pos = filename.rfind('.');
    if (std::string::npos != dot_pos)
        result = filename.substr(0, dot_pos);

    return result;
}

//-----------------------------------------------------------------------------
std::string AppendExtension(const std::string& filename, 
                            const FileFormat format)
{
    std::string result;

    switch (format)
    {
    case FileFormat::CSV:
        result = filename + EXT_CSV;
        break;
    case FileFormat::XML:
        result = filename + EXT_XML;
        break;
    case FileFormat::JSON:
        result = filename + EXT_JSON;
        break;
    case FileFormat::TXT:
        result = filename + EXT_TXT;
        break;
    default:
        throw std::logic_error("AppendExtension: unknown file format");
    }

    return result;
}

//-----------------------------------------------------------------------------
std::string FileNameFromFilePath(const std::string& filepath)
{
    std::string result(filepath);

    // look for the final '/' character
    auto pathsep_pos = filepath.rfind('/');
    if (std::string::npos != pathsep_pos)
        result = filepath.substr(pathsep_pos + 1);
    
    return result;
}

//-----------------------------------------------------------------------------
bool CaseInsensitiveEquals(const std::string& lhs, const std::string& rhs)
{
    if (lhs.size() != rhs.size())
        return false;

    // return true if all chars match

    std::string allcaps_lhs(lhs);
    ToUpper(allcaps_lhs);

    std::string allcaps_rhs(rhs);
    ToUpper(allcaps_rhs);

    return (allcaps_lhs == allcaps_rhs);
}

//-----------------------------------------------------------------------------
bool FileExists(const std::string& filepath)
{
    // if the file can be successfully opened, it exists
    std::ifstream infile(filepath);
    if (!infile)
        return false;

    infile.close();
    return true;
}

//-----------------------------------------------------------------------------
std::string ElapsedTime(const uint64_t& elapsed_us)
{
    uint64_t US_PER_SEC = 1000000;
    uint64_t US_PER_MIN = 60*US_PER_SEC;
    uint64_t US_PER_HR  = 60*US_PER_MIN;

    uint64_t elapsed = elapsed_us;
    uint64_t hrs=0, min=0, sec=0;
    
    if (elapsed >= US_PER_HR)
    {
        hrs = elapsed / US_PER_HR;
        elapsed -= (hrs * US_PER_HR);
    }
    
    if (elapsed >= US_PER_MIN)
    {
        min = elapsed / US_PER_MIN;
        elapsed -= (min * US_PER_MIN);
    }
    
    if (elapsed >= US_PER_SEC)
    {
        sec = elapsed / US_PER_SEC;
        elapsed -= (sec * US_PER_SEC);
    }

    double seconds = (double)sec + elapsed/1.0e6;

    char buf[256];
    if (hrs > 0)
    {
        sprintf(buf, "%d hours %d min %.3f sec.", 
                (int)hrs, (int)min, seconds);
    }
    else if (min > 0)
    {
        sprintf(buf, "%d min %.3f sec.", (int)min, seconds);
    }
    else
    {
        sprintf(buf, "%.3f sec.", seconds);
    }

    return std::string(buf);
}

//-----------------------------------------------------------------------------
bool LoadStringsFromFile(const std::string& filepath,
                         std::vector<std::string>& strings)
{
    std::ifstream instream(filepath);
    if (!instream)
        return false;

    // read the complete line, even if it contains several words
    std::string line;
    while (instream)
    {
        std::getline(instream, line, '\n');
        if (instream.eof())
            break;
        strings.push_back(line);
    }

    instream.close();
    return true;
}

//-----------------------------------------------------------------------------
void InvalidArg(const std::string& arg)
{
    std::string msg("Invalid command-line argument: ");
    msg += arg;
    throw std::runtime_error(msg);
}

//-----------------------------------------------------------------------------
void InvalidValue(const std::string& arg)
{
    std::string msg("Invalid value specified for command-line argument ");
    msg += arg;
    throw std::runtime_error(msg);
}
