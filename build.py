#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default
from conans import tools


if __name__ == "__main__":
    builder = build_template_default.get_builder(pure_c=False)

    if tools.os_info.is_windows:
        filtered_builds = []
        for settings, options, env_vars, build_requires, reference in builder.items:
            if "MT" not in settings["compiler.runtime"]:
                filtered_builds.append([settings, options, env_vars, build_requires])
        builder.builds = filtered_builds

    builder.run()
