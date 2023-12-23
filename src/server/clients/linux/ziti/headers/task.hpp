#ifndef __TASK_H__INCLUDED__
#define __TASK_H__INCLUDED__

#include <nlohmann/json.hpp>
#include <iostream>
#include <string>

#include "globals.hpp"

using namespace nlohmann;

class Pottask
{
  public:
    TASK_STATUS readTask();
    void addLog(json json_object, std::string command_output);
    void uploadLog();
    TASK_TYPE switchTask(json input_task);
}

#endif