"""
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) 2024  Zoran Kaufmann, Syndicat Mixte d'Aménagement de la Vallée de la Durance (SMAVD)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
"""
Module principal
"""
#-----------------------------------------------------------
# Copyright (C) 2015 Martin Dobias
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------
from typing import Any
from pathlib import Path
from PyQt5.QtWidgets import QAction, QMessageBox, QComboBox
from PyQt5.QtCore import Qt
from qgis.utils import iface
from qgis.core import Qgis, QgsMapLayerType, QgsProject, QgsMapLayer
from PyQt5.QtGui import QIcon
from synchro_retour_terrain.window_retour_terrain import WindowRetourTerrain # Vs Code ne trouve pas le module situé dans le même dossier mais Qgis le trouvera bien. 


def classFactory(iface):

    # Choisir quelle version du plugin utiliser

    return SyncRetourTerrainPlugin(iface)


class SyncRetourTerrainPlugin:
    """
    Classe principale de mon super plugin
    """

    def __init__(self, iface : Any) -> None:
        self.iface = iface
        self.action = None   

    def initGui(self) -> None:
        # chemin vers l'icone : 
        plugin_dir = Path(__file__).parent
        icon_path = plugin_dir / 'icon.png'
        # Creer l'action dans la barre de menu
        self.action = QAction(QIcon(str(icon_path)), "Synchro retour terrain", self.iface.mainWindow())
        # Ajouter un bouton de cette action dans la barre d'outils de QGIS des Extensions
        self.iface.addToolBarIcon(self.action)

        # Lier l'activation de l'action l'ouverture de la fenêtre
        self.action.triggered.connect(self.run_plugin)




    def run_plugin(self):
        ''' Méthode qui permet de générer la fenetre du plugin'''
        # On crée l'objet fenetre_principale
        self.fenetre_principale = WindowRetourTerrain(self.iface.mainWindow())  
        # Charger MapLayerCombobox_target
        self.fenetre_principale.populate_targetcombobox()   # Ou utilisez le flag approprié pour filtrer par type
        # Si la couche courrante de MapLayerComboBox_target n'est pas nulle, on récupère les attributs de la couche cible pour alimenter idu_comboBox grace à get_target_fields
        if self.fenetre_principale.MapLayerComboBox_target.currentLayer() != None:
            self.fenetre_principale.get_target_fields(self.fenetre_principale.MapLayerComboBox_target.currentLayer(), self.fenetre_principale.idu_comboBox)
        # Si la couche courrante de MapLayerComboBox_target n'est pas nulle, on récupère les attributs de la couche cible pour alimenter date_comboBox grace à get_target_fields
        if self.fenetre_principale.MapLayerComboBox_target.currentLayer() != None:
            self.fenetre_principale.get_target_fields(self.fenetre_principale.MapLayerComboBox_target.currentLayer(), self.fenetre_principale.date_combobox, "date_maj")
        # On connecte les boutons
        self._connectSlots()
        #print('run est bien connecté')
        # On affiche la fenetre principale
        self.fenetre_principale.show()

    
    def _connectSlots(self):
        '''Méthode pour connecter les signaux aux bonnes méthodes'''
        #connection du signal accepted de l'OBJET fenetre_principale à la fonction update_data. 
        self.fenetre_principale.accepted.connect(self.fenetre_principale.update_data)
        # Connection du signal fileChaged du mQgsFileWidget_source a la méthode check_soruce_format
        self.fenetre_principale.mQgsFileWidget_source.fileChanged.connect(self.fenetre_principale.check_source_format)
        # Connection de populat_targetcombobox() au signal de changement des couches chargées dans le projet
        self.iface.mapCanvas().layersChanged.connect(self.fenetre_principale.populate_targetcombobox)
        #connection de la idu_combobox au signal de changement de couche de MapLayerComboBox_target
        self.fenetre_principale.MapLayerComboBox_target.layerChanged.connect(
            lambda: self.fenetre_principale.get_target_fields(self.fenetre_principale.MapLayerComboBox_target.currentLayer(), self.fenetre_principale.idu_comboBox)
            )
        #connection de la date_combobox au signal de changement de couche de MapLayerComboBox_target
        self.fenetre_principale.MapLayerComboBox_target.layerChanged.connect(
            lambda: self.fenetre_principale.get_target_fields(self.fenetre_principale.MapLayerComboBox_target.currentLayer(), self.fenetre_principale.date_combobox, "date_maj")
            )


    def unload(self) -> None:
        """
        Cette méthode est appelée lorsque le plugin est désactivé
        (décoché dans le gestionnaire d'extensions) ou désinstallé
        """
        # On enlève le bouton de la barre d'outils
        self.iface.removeToolBarIcon(self.action)
        # On supprime l'objet action
        del self.action
    

     



