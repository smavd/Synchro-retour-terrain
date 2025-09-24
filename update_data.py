'''
####################################################################################################
Description du programme 
Le script permet de mettre à jour une couche cible du Projet Qgis principal à partir d'une couche source du projet Qfield. 
Les couches doivent avoir un identiufiant unique (IDU) qui sert de clef primaire. Ce champ doit être rempli automatiquement lors de la création d'entités.
Les couches sources et cibles doivent avoir la même structure. 
La couche cible est mise à jour selon les règles suivantes : 
    -l'IDU existe déjà dans la couche cible : la ligne est mise à jour si le script détecte un changement dans les attributs. 
    -l'IDU n'existe pas dans la couche cible : la ligne est copiée depuis la couche source vers la couche cible. 

Date : juillet 2024
Auteur : clément Dutremble / SMAVD (clement.dutremble@smavd.org)

To do :
- Prévoir une mQgsExternalResourceWidget piur la source_layer
- Verifier la conccordance des champs et des typês entre source_layer et target_layer
- laisser le choix de l'identifiant unique (IDU par défaut)
####################################################################################################
'''
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel
from qgis.core import QgsProject, QgsMapLayerType, QgsFeature, QgsSpatialIndex, QgsWkbTypes

class LayerUpdater:
    @staticmethod
    def update_layers(source_layer, target_layer):
        # Vérifier l'existence des champs IDU dans les couches
        source_field_idx = source_layer.fields().indexOf('IDU')
        target_field_idx = target_layer.fields().indexOf('IDU')

        if source_field_idx == -1 or target_field_idx == -1:
            print("Le champ IDU n'existe pas dans une des couches")
            return

        target_layer.startEditing()

        # Créer un index pour rechercher les entités par IDU
        target_idu_index = {}
        for target_feature in target_layer.getFeatures():
            target_idu_index[target_feature['IDU']] = target_feature

        for source_feature in source_layer.getFeatures():
            source_idu_value = source_feature['IDU']

            # Vérifier si l'entité existe déjà dans la couche cible
            if source_idu_value in target_idu_index:
                target_feature = target_idu_index[source_idu_value]
                update_required = False

                # Comparer les attributs
                for field in source_layer.fields():
                    if field.name() != 'fid' and source_feature[field.name()] != target_feature[field.name()]:
                        update_required = True
                        break

                # Mettre à jour l'entité cible si nécessaire
                if update_required:
                    for field in source_layer.fields():
                        if field.name() != 'fid':  # Inclure IDU
                            target_feature.setAttribute(field.name(), source_feature[field.name()])

                    # Mettre à jour la géométrie
                    if source_layer.geometryType() != QgsWkbTypes.NullGeometry:
                        target_feature.setGeometry(source_feature.geometry())

                    target_layer.updateFeature(target_feature)
            else:
                # Ajouter une nouvelle entité à la couche cible
                new_feature = QgsFeature(target_layer.fields())

                # Copier tous les attributs de la source vers la nouvelle entité
                for field in source_layer.fields():
                    if field.name() != 'fid':  # Inclure IDU
                        new_feature.setAttribute(field.name(), source_feature[field.name()])

                # Copier la géométrie de la source vers la nouvelle entité
                if source_layer.geometryType() != QgsWkbTypes.NullGeometry:
                    new_feature.setGeometry(source_feature.geometry())

                # Ajouter la nouvelle entité à la couche cible
                if not target_layer.addFeature(new_feature):
                    print(f"Impossible d'ajouter une nouvelle entité avec IDU {source_idu_value} à la couche cible.")

        # Valider et sauvegarder les modifications dans la couche cible
        if not target_layer.commitChanges():
            print("Erreur lors de la validation des modifications dans la couche cible.")

class LayerSelectorDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sélectionner des couches")

        self.layout = QVBoxLayout(self)

        # Label pour la couche source
        self.source_label = QLabel("Sélectionner la couche source :", self)
        self.layout.addWidget(self.source_label)

        self.source_combo = QComboBox(self)
        self.populate_layer_combo()
        self.layout.addWidget(self.source_combo)

        # Label pour la couche cible
        self.target_label = QLabel("Sélectionner la couche cible :", self)
        self.layout.addWidget(self.target_label)

        self.target_combo = QComboBox(self)
        self.populate_layer_combo()
        self.layout.addWidget(self.target_combo)

        self.select_button = QPushButton("Sélectionner", self)
        self.select_button.clicked.connect(self.accept)
        self.layout.addWidget(self.select_button)

        self.setLayout(self.layout)
    
    def populate_layer_combo(self):
        '''
        méthode qui parcoure les couches du projet et ajouter les couches valides (vecteur et tables) aux QcomboBox 
        de sélection des target_layer et source_layer
        '''
        # Lister toutes les couches du projet
        layers = QgsProject.instance().mapLayers().values()
        '''
        # Parcourir les couches et teste s'il s'agit de tables ou de vecteurs
        for layer in layers:
            try:
                if layer.type() == QgsMapLayerType.VectorLayer:
                    self.source_combo.addItem(layer.name(), layer)
                    self.target_combo.addItem(layer.name(), layer)
                elif layer.type() == QgsMapLayerType.Table:
                    if layer.isValid():
                        self.source_combo.addItem(layer.name(), layer)
                        self.target_combo.addItem(layer.name(), layer)
            except AttributeError as e:
                #print(f"Erreur lors du traitement de la couche {layer.name()}: {str(e)}")
                continue'''
                
    # Retourne la couche source selectionnée dans la combobox 
    def selected_source_layer(self):
        index = self.source_combo.currentIndex()
        return self.source_combo.itemData(index) if index >= 0 else None
    # Retourne la couche target selectionnée dans la combobox 
    def selected_target_layer(self):
        index = self.target_combo.currentIndex()
        return self.target_combo.itemData(index) if index >= 0 else None

# Création et exécution de la fenêtre de dialogue
dialog = LayerSelectorDialog()
if dialog.exec_():
    source_layer = dialog.selected_source_layer()
    target_layer = dialog.selected_target_layer()
     
    if source_layer and target_layer:
        # Appeler la méthode pour mettre à jour les couches
        LayerUpdater.update_layers(source_layer, target_layer)
else:
    print("L'utilisateur a annulé la sélection.")


