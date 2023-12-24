#ifndef __LOCAL_H__INCLUDED__
#define __LOCAL_H__INCLUDED__

#include <boost/algorithm/string/erase.hpp>
#include <ctime>
#include <iostream>
#include <string>

class Potlocal
{
  public:
    static std::string getTime();
    static std::string passCommand(std::string command);
    static void fingerprint();
    static int getUID();
    static int checkDisk(std::string folder_path);
};

#endif
