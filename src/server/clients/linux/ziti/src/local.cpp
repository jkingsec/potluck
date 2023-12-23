#include <boost/algorithm/string/erase.hpp>
#include <ctime>
#include <iostream>
#include <string>

#include "local.hpp"
#include "globals.hpp"

////LOCAL FUNCS
//get utctime
std::string Potlocal::getTime()
{
    //might be a way to format this a little cleaner, but it works fine
    std::time_t time = std::time({});
    char time_string[std::size("dd-mm-yyyy hh:mm:ss")];
    std::strftime(std::data(time_string), std::size(time_string),
        "%d-%m-%Y %H:%M:%S", std::gmtime(&time));
    return time_string;
}
//pass command
std::string Potlocal::passCommand(std::string command)
{
    //detect if command only outputs to stderr and throw exception
    std::string command_output;
    std::array<char, 128> buffer{};
    std::unique_ptr<FILE, decltype(&pclose)> pipe{
        popen(command.c_str(), "r"),
        pclose
    };
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        command_output += buffer.data();
    }
    return command_output;
}
//fingerprint
void Potlocal::fingerprint()
{
    user_name = passCommand("whoami");
    boost::algorithm::erase_all(user_name, "\n");
    host_name = passCommand("hostname");
    boost::algorithm::erase_all(host_name, "\n");
    os_name = passCommand("lsb_release -d | awk '{print $2,$3}'");
    boost::algorithm::erase_all(os_name, "\n");
    client_name = user_name + "@" + host_name;
    //

    //
    std::cout << "fingerprint done" << std::endl;
}
int Potlocal::getUID()
{
    client_UID = std::stoi(passCommand("id -u"));
    return client_UID;
}
int Potlocal::checkDisk(std::string folder_path)
{
   return std::stoi(passCommand("cat /sys/block/$(df " + folder_path +
   " | grep -oP '(?<=dev/)[[:alpha:]]*')/queue/rotational"));
}