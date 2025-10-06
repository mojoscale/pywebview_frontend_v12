#include <ESPAsyncWebServer.h>
#include <AsyncTCP.h>

// Custom wrapper for server.on()
// - Accepts both String or const char* for URI
// - Accepts "get"/"GET"/"POST"/"post" etc. case-insensitively
// - Returns void
void async_server_on(
    AsyncWebServer& server,
    const String& uri_str,
    const String& method_str,
    ArRequestHandlerFunction onRequest,
    ArUploadHandlerFunction onUpload = nullptr,
    ArBodyHandlerFunction onBody = nullptr
) {
    // Normalize the URI and method strings
    String uri = uri_str;
    String methodUpper = method_str;
    methodUpper.toUpperCase();

    WebRequestMethodComposite method = HTTP_ANY;  // Default fallback

    if (methodUpper == "GET") method = HTTP_GET;
    else if (methodUpper == "POST") method = HTTP_POST;
    else if (methodUpper == "PUT") method = HTTP_PUT;
    else if (methodUpper == "DELETE") method = HTTP_DELETE;
    else if (methodUpper == "PATCH") method = HTTP_PATCH;
    else if (methodUpper == "ANY") method = HTTP_ANY;

    // Call the real ESPAsyncWebServer::on() with proper conversions
    server.on(uri.c_str(), method, onRequest, onUpload, onBody);
}
