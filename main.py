# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MainApp
                                 A QGIS plugin
 Zoom to the extent of all layers
                              -------------------
        begin                : 2017-04-08
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Florian Blas
        email                : florian.blas@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from main_dialog import MainAppDialog
import os.path
from qgis.core import QgsMapLayerRegistry, QgsCoordinateTransform


class MainApp:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MainApp_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Zoom to all layers')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'MainApp')
        self.toolbar.setObjectName(u'MainApp')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('MainApp', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = MainAppDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/MainApp/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Zoom to all layers'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Zoom to all layers'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""
        if len(QgsMapLayerRegistry.instance().mapLayers().values()) > 0:
            self.select_all_layers()
            self.zoom_to_selection()
            self.deselect_all_layers()

    def select_all_layers(self):
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if layer.type() == 0:
                layer.selectAll()   # select all features

    def deselect_all_layers(self):
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if layer.type() == 0:
                layer.removeSelection()

    def zoom_to_selection(self):
        rects = self.get_bounding_boxes()
        for rect in rects:
            rects[0].combineExtentWith(rect)    # Combine first extent with the others
        self.iface.mapCanvas().setExtent(rects[0])

    def adjust_rect_to_crs(self, layer, rectangle):
        coord_trans = QgsCoordinateTransform()
        coord_trans.setSourceCrs(layer.crs())
        coord_trans.setDestCRS(self.iface.mapCanvas().mapSettings().destinationCrs())
        return coord_trans.transform(rectangle)

    def get_bounding_boxes(self):
        rects = []
        for l in QgsMapLayerRegistry.instance().mapLayers().values():
            if l.type() == 0:
                rect = l.boundingBoxOfSelected()
                if not l.crs() == self.iface.mapCanvas().mapSettings().destinationCrs():
                    rect = self.adjust_rect_to_crs(l, rect)
                rects.append(rect)
        return rects

