#ifndef PYWEBSERVER_ESP32_FACTORY_H
#define PYWEBSERVER_ESP32_FACTORY_H

#include <WebServer.h>
#include <memory>

class PyWebServer {
private:
    std::unique_ptr<WebServer> server;
    int _port = 80;

    PyWebServer() = default;

public:
    // Provide access to a single static instance
    static PyWebServer& get() {
        static PyWebServer instance;
        return instance;
    }

    PyWebServer& port(int port) {
        _port = port;
        return *this;
    }

    WebServer& init() {
        server = std::make_unique<WebServer>(_port);
        server->begin();
        return *server;
    }
};





#endif
