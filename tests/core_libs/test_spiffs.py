import spiffs as sp


def setup() -> None:
    sp_begin = sp.spiffs_begin()

    sp.spiffs_end()

    sp_format_succeed = sp.spiffs_format()

    sp.spiffs_open("/", "r")

    does_spiffs_exist = sp.spiffs_exists("/")

    was_removed = sp.spiffs_remove("/test")

    was_renamed = sp.spiffs_rename("/pre", "/post")

    was_mkdir_done = sp.spiffs_mkdir("/new_dir")

    was_rmdir = sp.spiffs_rmdir("/new_dir")

    used_bytes = sp.spiffs_used_bytes()

    total_bytes = sp.spiffs_total_bytes()

    free_bytes = sp.spiffs_free_bytes()

    spiffs_infor = sp.spiffs_info()


def loop() -> None:
    pass
