#ifndef __PERSIST_H__INCLUDED__
#define __PERSIST_H__INCLUDED__

#include <iostream>
#include <string>

class Potpersist
{
  public:
    static bool checkPersist();
    static void setPersist(char* arg_string);
    static void removePersist();
};

#endif
