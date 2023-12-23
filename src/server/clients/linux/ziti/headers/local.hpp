#ifndef __LOCAL_H__INCLUDED__
#define __LOCAL_H__INCLUDED__

#include <boost/algorithm/string/erase.hpp>
#include <ctime>
#include <iostream>
#include <string>

class Potlocal
{
  public:
    std::string getTime();
    std::string passCommand(std::string command);
    void fingerprint();
    int getUID();
    int checkDisk(std::string folder_path);
}

#endif
