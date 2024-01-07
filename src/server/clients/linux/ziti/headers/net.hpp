#ifndef __NET_H__INCLUDED__
#define __NET_H__INCLUDED__

#include <iostream>
#include <string>
#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>

#include "globals.hpp"

namespace beast = boost::beast;
namespace http = beast::http;

class Potnet 
{
public:
  struct res_struct {
    RES_STATUS res_stat; 
    http::response<http::basic_string_body<char>> res_body;
  };
  static res_struct getRequest(std::string target);
  static res_struct postRequest(std::string target, std::string body_data);
  static void ping();
  static bool checkListener();
};

#endif