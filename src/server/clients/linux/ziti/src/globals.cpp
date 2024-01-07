#include <nlohmann/json.hpp>
#include <iostream>
#include <string>

#include "globals.hpp"

using namespace nlohmann;

//VARIABLES ARE SET BY GENERATOR

//net variables
std::string host = "";
std::string port = "";
int version = 11; //change to 20?

json listener_json = json::parse(R"()");

//Vars
//static client id
std::string client_id = "";
//project id
std::string project_id = "";
//expiration date
std::string expiration_date = "";
//task array
json task_array = json::array();
//log array
json log_array = json::array();
//settings
bool NO_VM = true;
bool PERSIST_ON = false;
//connection bool
bool CONN_OK = false;

//placeholders
//os name
std::string os_name = "";
//user name
std::string user_name = "";
//hostname
std::string host_name = "";
//client name
std::string client_name = "";
//UID
int client_UID = 1000;
//sleep time
int sleep_time = 15;