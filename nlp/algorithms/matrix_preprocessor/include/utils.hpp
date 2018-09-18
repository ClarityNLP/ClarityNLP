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

#include <iostream>
#include <string>
#include <vector>
#include <cstdint>
#include "file_format.hpp"

// convert an ASCII string in place
void ToUpper(std::string& str);
void ToLower(std::string& str);

// trim single and/or double quotes from the string str
std::string TrimQuotes(const std::string& str);

// add a path separator to the string if not present
std::string EnsureTrailingPathSep(const std::string& str);

// given a filename return the file extension (everything after the final '.')
std::string FileExtension(const std::string& filename);

// given a filename remove the extension
std::string TrimExtension(const std::string& filename);

// return a string with the extension for the given format appended
std::string AppendExtension(const std::string& filename, 
                            const FileFormat format);

// given a fully-qualified path to a matrix file, return only the filename
std::string FileNameFromFilePath(const std::string& filepath);

// do a case-insensitive string comparison
bool CaseInsensitiveEquals(const std::string& lhs, const std::string& rhs);

std::string ElapsedTime(const uint64_t& elapsed_us);

// check to see if a directory exists
bool DirectoryExists(const std::string& dir);

// check to see if a file exists
bool FileExists(const std::string& filepath);

// Get and set the current directory. If the function fails, the dir string
// contains an error message and the function returns false.
bool GetCurrentDirectory(std::string& dir);
bool SetCurrentDirectory(std::string& dir);

// load a file consisting entirely of strings
bool LoadStringsFromFile(const std::string& filepath,
                         std::vector<std::string>& strings);

// for help with command-line parsing
void InvalidArg(const std::string& arg);
void InvalidValue(const std::string& arg);
