#ifndef PYWEBSERVER_ESP8266_FACTORY_H
#define PYWEBSERVER_ESP8266_FACTORY_H

#include <ESP8266WebServer.h>
#include <memory>

class PyWebServer {
private:
    std::unique_ptr<ESP8266WebServer> server;
    int _port = 80;

public:
    PyWebServer() = default;

    PyWebServer& port(int port) {
        _port = port;
        return *this;
    }

    ESP8266WebServer& init() {
        server = std::make_unique<ESP8266WebServer>(_port);
        server->begin();
        return *server;
    }
};



#endif
