Import("env")

import os
from os.path import join, isfile
import hashlib


def _file_long_data_workaround(env, _data):
    data = env.subst(_data).replace("\\", "/")
    build_dir = env.subst("$BUILD_DIR")
    tmp_file = join(build_dir, "longcmd-%s" % hashlib.md5(data.encode()).hexdigest())
    if not isfile(tmp_file):
        with open(tmp_file, "w") as fp:
            fp.write(data)
    return '@"%s"' % tmp_file


def apply_clean_linker():
    # Full safe override — ignore whatever PlatformIO injected
    clean_linkcom = (
        "${TEMPFILE('$LINK -o $TARGET "
        "$LINKFLAGS $__RPATH $SOURCES $_LIBDIRFLAGS $_LIBFLAGS')}"
    )

    env.Replace(LINKCOM=clean_linkcom)
    env.Replace(_long_libflags_hook=_file_long_data_workaround)

    # Apply hook into $_LIBFLAGS
    env.Replace(
        LINKCOM=env.get("LINKCOM").replace(
            "$_LIBFLAGS", "${_long_libflags_hook(__env__, _LIBFLAGS)}"
        )
    )

    print("Forced clean LINKCOM (Windows safe override)")


apply_clean_linker()
