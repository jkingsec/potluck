#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/beast/version.hpp>
#include <boost/asio/connect.hpp>
#include <boost/asio/ip/tcp.hpp>

#include <nlohmann/json.hpp>

#include "net.hpp"
#include "local.hpp"
#include "globals.hpp"

namespace beast = boost::beast;
namespace http = beast::http;
namespace net = boost::asio;
using tcp = net::ip::tcp;
using namespace nlohmann;

//net stuff
net::io_context ioc;
tcp::resolver resolver(ioc);
beast::tcp_stream stream(ioc);

beast::error_code ec;
beast::flat_buffer buffer;

////NET FUNCS
//get
Potnet::res_struct Potnet::getRequest(std::string target)
{
http::response<http::string_body> res;
Potnet::res_struct final_result;
try
    {
        auto results = resolver.resolve(host, port);

        stream.connect(results);

        http::request<http::string_body> req{http::verb::get, target, version};
        req.set(http::field::host, host);

        http::write(stream, req);

        http::read(stream, buffer, res);

        stream.socket().shutdown(tcp::socket::shutdown_both, ec);

        final_result.res_stat = RES_SUCCESS;
        final_result.res_body = res;
        return final_result;
    }
    catch(std::exception const& e)
    {
        std::cerr << "Error: " << e.what() << std::endl;
        //return EXIT_FAILURE;
        CONN_OK = false;
        final_result.res_stat = RES_FAIL;
        final_result.res_body = res;
        return final_result;
    }
    std::cout << "getRequest done" << std::endl;
}
//post
Potnet::res_struct Potnet::postRequest(std::string target, std::string body_data)
{
http::response<http::string_body> res; //if error, body is empty
Potnet::res_struct final_result;
try
    {
        auto results = resolver.resolve(host, port);

        stream.connect(results);

        http::request<http::string_body> req{http::verb::post, target, version};
        req.set(http::field::content_type, "application/x-www-form-urlencoded");
        req.set(http::field::host, host);

        req.body() = body_data;
        req.prepare_payload();

        http::write(stream, req);

        http::read(stream, buffer, res);

        stream.socket().shutdown(tcp::socket::shutdown_both, ec);
        final_result.res_stat = RES_SUCCESS;
        final_result.res_body = res;
        return final_result;
    }
    catch(std::exception const& e)
    {
        std::cerr << "Error: " << e.what() << std::endl;
        CONN_OK = false;
        //return EXIT_FAILURE;
        final_result.res_stat = RES_SUCCESS;
        final_result.res_body = res;
        return final_result;
    }
    std::cout << "postRequest done" << std::endl;
}
//ping
void Potnet::ping()
{
    //try/catch
    json ping_data;
    ping_data["client_name"] = client_name;
    ping_data["client_os"] = os_name;
    ping_data["send_time"] = Potlocal::getTime();
    ping_data["client_settings"] = "{}";
    ping_data["project_id"] = project_id;
    postRequest(
        "/clients/" + client_id,
        "data="+ping_data.dump()
    );
    std::cout << "ping done" << std::endl;
    //return bool
}
//check listener
bool Potnet::checkListener()
{
    while (CONN_OK != true)
    {
        std::cout<< CONN_OK <<std::endl;
        for (const auto& listener : listener_json.items())
        {
            host = listener.value()["host"];
            port = listener.value()["port"];
            std::cout << host + port << std::endl;
            Potnet::res_struct result = getRequest("/");
            if ( result.res_stat == RES_SUCCESS && result.res_body.result() == http::status::ok)//this isn't working
            //if using a custom struct, have if SUCCESS && res.result() == http::status::ok
            {
                CONN_OK = true;
                goto CHECK_PASSED;
            }
        }
        sleep(15);//need to change to a few minutes or something
    }
    CHECK_PASSED: {}
    return true;
}