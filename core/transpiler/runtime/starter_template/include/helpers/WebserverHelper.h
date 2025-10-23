#ifndef PYWEBSERVER_FACTORY_H
#define PYWEBSERVER_FACTORY_H

#ifdef ESP8266
    #include <ESP8266WebServer.h>
#elif defined(ESP32)
    #include <WebServer.h>
#endif

#include <memory>
#include <functional>

// Custom helper function for registering routes
void custom_webserver_on(
#ifdef ESP8266
    ESP8266WebServer& server,
#elif defined(ESP32)
    WebServer& server,
#endif
    const String& path, 
    const String& method, 
    std::function<void()> handler
) {
    if (method == "HTTP_GET") {
        server.on(path, HTTP_GET, handler);
    } else if (method == "HTTP_POST") {
        server.on(path, HTTP_POST, handler);
    } else if (method == "HTTP_PUT") {
        server.on(path, HTTP_PUT, handler);
    } else if (method == "HTTP_DELETE") {
        server.on(path, HTTP_DELETE, handler);
    } else if (method == "HTTP_PATCH") {
        server.on(path, HTTP_PATCH, handler);
    } else {
        // Default to GET if method not recognized
        server.on(path, HTTP_GET, handler);
    }
}

class PyWebServer {
private:
#ifdef ESP8266
    std::unique_ptr<ESP8266WebServer> server;
#elif defined(ESP32)
    std::unique_ptr<WebServer> server;
#endif
    
    int _port = 80;

public:
#ifdef ESP8266
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

#elif defined(ESP32)
    PyWebServer() = default;

    // Provide access to a single static instance for ESP32
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
#endif
};

#endif