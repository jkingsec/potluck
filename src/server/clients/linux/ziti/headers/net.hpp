#ifndef __NET_H__INCLUDED__
#define __NET_H__INCLUDED__

#include <iostream>
#include <string>
#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>

namespace beast = boost::beast;
namespace http = beast::http;

class Potnet 
{
public:
  struct res_struct {
    RES_STATUS res_stat; 
    http::response<http::basic_string_body<char>> res_body;
  };
  res_struct  getRequest(std::string target);
  res_struct postRequest(std::string target, std::string body_data);
  void ping();
  bool checkListener();
}

#endif