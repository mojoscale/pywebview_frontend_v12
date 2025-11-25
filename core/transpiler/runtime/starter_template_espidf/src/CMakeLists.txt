idf_component_register(
    SRCS
        "app_main.cpp"
        "main.cpp"                  # <-- Your transpiled Arduino entrypoint
    INCLUDE_DIRS "."
    REQUIRES arduino
)
