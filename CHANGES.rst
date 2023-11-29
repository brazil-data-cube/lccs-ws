..
    This file is part of LCCS-WS.
    Copyright (C) 2022 INPE.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.


=======
Changes
=======

Version 0.8.0 (2022-02-07)
--------------------------

- Upgrade to lccs-db 0.8.0 dependency (`#71 <https://github.com/brazil-data-cube/lccs-ws/issues/71>`_).
- Add supported languages in API root (`#74 <https://github.com/brazil-data-cube/lccs-ws/issues/74>`_).
- Improve API resource links (`#73 <https://github.com/brazil-data-cube/lccs-ws/issues/73>`_).
- Add support I18N with lccs-db (`#72 <https://github.com/brazil-data-cube/lccs-ws/issues/72>`_).
- Upgrade Oauth2 library (bdc-auth-client) to 0.2.3 (`#71 <https://github.com/brazil-data-cube/lccs-ws/issues/71>`_).


Version 0.6.0 (2021-04-09)
--------------------------

- Add Drone CI support (`#44 <https://github.com/brazil-data-cube/lccs-ws/issues/44>`_)

- Add git submodule (`#28 <https://github.com/brazil-data-cube/lccs-ws/issues/28>`_)

- Remove dependency of bdc-core and flask-restplus (`#36 <https://github.com/brazil-data-cube/lccs-ws/issues/36>`_)

- Integrate with BDC-Auth (`#40 <https://github.com/brazil-data-cube/lccs-ws/issues/40>`_)

- Add automatic deploy on dev and production sites (`#50 <https://github.com/brazil-data-cube/lccs-ws/issues/50>`_)

- Update operations based on Spec 0.6  (`#51 <https://github.com/brazil-data-cube/lccs-ws/issues/51>`_)

- Improve error handler (`#55 <https://github.com/brazil-data-cube/lccs-ws/issues/55>`_)

- Bug fix: Fix parent link in classification_system (`#41 <https://github.com/brazil-data-cube/lccs-ws/issues/41>`_)

- Bug fix: Failed to find attribute 'app' in 'lccs_ws' in Dockerfile (`#63 <https://github.com/brazil-data-cube/lccs-ws/issues/63>`_)

- Upgrade lccs-db to 0.6.0 (`#66 <https://github.com/brazil-data-cube/lccs-ws/issues/66>`_)


Version 0.4.0-1 (2021-01-13)
----------------------------


- Bug fix: Review links in the classification_system route (`#41 <https://github.com/brazil-data-cube/lccs-ws/issues/41>`_)


Version 0.4.0-0 (2020-12-16)
----------------------------


- Compatibility with `LCC-DB Version 0.4.0 <https://github.com/brazil-data-cube/lccs-db>`_.

- Support for the `LCCS-WS specification version 0.4.0-0 <https://github.com/brazil-data-cube/lccs-ws-spec>`_.

- Improved Sphinx template.

- Fixed small typos in documentation.


Version 0.2.0 (2020-04-16)
--------------------------


- First experimental version.

- Support for: Class Systems, Classes, Styles and Class Mappings.

- Support for the `LCCS-WS specification version 0.2.0 <https://github.com/brazil-data-cube/lccs-ws-spec>`_.

- Compatibility with `LCC-DB Version 0.2.0 <https://github.com/brazil-data-cube/lccs-db>`_.

- Documentation system based on Sphinx.

- Documentation integrated to ``Read the Docs``.

- Package support through Setuptools.

- Installation and use instructions.

- Support for dynamic loading of model classes derived from LCCS-DB.

- Source code versioning based on `Semantic Versioning 2.0.0 <https://semver.org/>`_.

- License: `MIT <https://raw.githubusercontent.com/brazil-data-cube/lccs-ws/v0.2.0-0/LICENSE>`_.
