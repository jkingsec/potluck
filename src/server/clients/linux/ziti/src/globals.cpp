#include <nlohmann/json.hpp>
#include <iostream>
#include <string>

#include "globals.hpp"

using namespace nlohmann;

//net variables
std::string host = "localhost";
std::string port = "5150";
int version = 11; //change to 20?
//change to struct or seperate variables. should only parse incoming json
json listener_json = json::parse(R"([
{"host": "localhost", "port": "5150"},
{"host": "localhost", "port": "5151"},
{"host": "localhost", "port": "5152"}])"); //going to be a problem with the template script

//Vars
//static client id
std::string client_id = "00000000-0000-0000-0000-000000000000";//replace with generated uuid or read from persistence
//project id
int project_id = 1;//replace
//expiration date
std::string expiration_date = "11-11-2111"; //replace
//os name
std::string os_name;
//user name
std::string user_name;
//hostname
std::string host_name;
//client name
std::string client_name;
//UID
int client_UID;
//task array
json task_array;
//log array
json log_array = json::array();
//log output
std::string log_output;
//settings
bool NO_VM = true;
bool PERSIST_ON = false;//for testing purposes
//enums
enum TASK_STATUS { NOTASK, TASK, CONNERROR };
enum TASK_TYPE {COMMAND, CONFIG, PERSIST, PING, SHUTDOWN, DELETE};
enum RES_STATUS { RES_SUCCESS, RES_FAIL };
//connection bool
bool CONN_OK = false;