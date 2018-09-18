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

#include <random>
#include <string>
#include <sstream>
#include <cassert>

class Random
{
public:
    
    Random() {}

    // Seed the RNG by various methods; std::random_device may not
    // exist on all systems, so need to verify existence before calling.

    // SeedFromTime has a resolution of 1 second, so do not call more than
    // once per second.
    void SeedFromTime();
    void SeedFromRandomDevice();   // be careful - may not exist on all systems
    void SeedFromInt(const int s);

    // manipulate the engine state
    void SetDefaultState();
    std::string GetState();
    void SetState(const std::string& state);

    // Generate a random number of the indicated type on a maximal interval; 
    // the int function returns values on an INCLUSIVE interval, but the
    // others return on an interval open at the upper limit.
    int    RandomInt();    // [0,    std::numeric_limits<int>::max() ] 
    float  RandomFloat();  // [0.0f, 1.0f)
    double RandomDouble(); // [0.0,  1.0)

    // returns a random number on [a, b)
    int    RandomRangeInt   (const int&    a, const int&    b);
    float  RandomRangeFloat (const float&  a, const float&  b);
    double RandomRangeDouble(const double& a, const double& b);

    // returns a random number on (center - radius, center + radius)
    int    RandomInt   (const int&    center, const int&    radius);
    float  RandomFloat (const float&  center, const float&  radius);
    double RandomDouble(const double& center, const double& radius);

private:

    // Mersenne Twister engine
    std::mt19937 engine_;

    std::uniform_int_distribution<int>     dist_int_;
    std::uniform_real_distribution<float>  dist_float_;
    std::uniform_real_distribution<double> dist_double_;
};

//-----------------------------------------------------------------------------
inline
void Random::SeedFromInt(const int s)
{
    engine_.seed(s);
}

//-----------------------------------------------------------------------------
inline
void Random::SeedFromTime()
{
    engine_.seed( time(0) );
}

//-----------------------------------------------------------------------------
inline
void Random::SeedFromRandomDevice()
{
    std::random_device rd;
    engine_.seed(rd());
}

//-----------------------------------------------------------------------------
inline
void Random::SetDefaultState()
{
    engine_.seed();
}

//-----------------------------------------------------------------------------
inline
std::string Random::GetState()
{
    std::stringstream sstr;
    sstr << engine_;
    return sstr.str();
}

//-----------------------------------------------------------------------------
inline
void Random::SetState(const std::string& state)
{
    std::stringstream sstr(state);
    sstr >> engine_;
}

//-----------------------------------------------------------------------------
inline
int Random::RandomInt() 
{
    return dist_int_(engine_);
}

//-----------------------------------------------------------------------------
inline
float Random::RandomFloat()
{
    return dist_float_(engine_);
}

//-----------------------------------------------------------------------------
inline
double Random::RandomDouble() 
{
    return dist_double_(engine_);
}

//-----------------------------------------------------------------------------
inline
int Random::RandomInt(const int& center, const int& radius)
{
    assert(radius > 0);
    return center + (RandomInt() % (2*radius)) - radius;
}

//-----------------------------------------------------------------------------
inline
float Random::RandomFloat(const float& center, const float& radius)
{
    assert(radius > 0.0);
    return center + 2.0f*radius*RandomFloat() - radius;
}

//-----------------------------------------------------------------------------
inline
double Random::RandomDouble(const double& center, const double& radius)
{
    assert(radius > 0.0);
    return center + 2.0*radius*RandomDouble() - radius;
}

//-----------------------------------------------------------------------------
inline
int Random::RandomRangeInt(const int& a, const int& b)
{
    assert(b > a);
    return a + (RandomInt() % (b-a));
}

//-----------------------------------------------------------------------------
inline
float Random::RandomRangeFloat(const float& a, const float& b)
{
    assert(b > a);
    return a + (b-a)*RandomFloat();
}

//-----------------------------------------------------------------------------
inline
double Random::RandomRangeDouble(const double& a, const double& b)
{
    assert(b > a);
    return a + (b-a)*RandomDouble();
}

