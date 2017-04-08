# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MainApp
                                 A QGIS plugin
 Zoom to the extent of all layers
                             -------------------
        begin                : 2017-04-08
        copyright            : (C) 2017 by Florian Blas
        email                : florian.blas@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MainApp class from file MainApp.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .main import MainApp
    return MainApp(iface)
