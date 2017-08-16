
import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout

from qgis.core import NULL
from qgis.gui import QgsEditorWidgetWrapper, QgsEditorConfigWidget, QgsEditorWidgetFactory

from milstd2525.sidcdialog import SIDCDialog
from milstd2525.milstd2525symbology import symbolForCode


pluginPath = os.path.dirname(__file__)

'''
This loads the UI files dynamically, on the fly, so there is no need to 
compile ui files in advance.
'''
CONFIG_WIDGET, CONFIG_BASE = uic.loadUiType(
    os.path.join(pluginPath, 'ui', 'milstd2525configwidgetbase.ui'))


class SIDCWidgetWrapper(QgsEditorWidgetWrapper):
    '''
    This widget is used in the attribute table, to make it easier to enter
    MIL-STD-2525 codes when editing layer attributes. It contains a text box 
    that can be used to type the code, and a button that opens a dialog in 
    which codes can be edited graphically, selecting from a set of combo boxes 
    with parameters.
    '''
    def __init__(self, vl, fieldIdx, editor, parent):
        self.widget = None
        super(SIDCWidgetWrapper, self).__init__(vl, fieldIdx, editor, parent)

    def value( self ):
        '''This method returns the value to be set as attribute value, based on the widget value'''
        if self.widget.edit.text() == 'NULL':
            return NULL
        else:
            return self.widget.edit.text()

    def setValue(self, value):
        '''Changes the current value of the widget based on a passed value'''
        if value == NULL:
            self.widget.edit.setText('NULL')
        else:
            self.widget.edit.setText(value)

    def createWidget(self, parent):
        '''This method should return an instance of the widget'''
        self.widget = QWidget(parent)
        self.widget.edit = QLineEdit()
        self.widget.button = QPushButton()
        self.widget.button.setText("...")
        def showDialog():
            dialog = SIDCDialog(self.widget.edit.text())
            dialog.exec_()
            if dialog.newCode is not None:
                self.widget.edit.setText(dialog.newCode)
        self.widget.button.clicked.connect(showDialog)
        self.widget.hbox = QHBoxLayout()
        self.widget.hbox.setMargin(0)
        self.widget.hbox.setSpacing(0)
        self.widget.hbox.addWidget(self.widget.edit)
        self.widget.hbox.addWidget(self.widget.button)
        self.widget.setLayout(self.widget.hbox)
        return self.widget

    def initWidget(self, editor):
        self.widget = editor

    def valid(self):
        return True


class SIDCWidgetWrapperConfig(QgsEditorConfigWidget, CONFIG_WIDGET):
    def __init__(self, layer, idx, parent):
        super(SIDCWidgetWrapperConfig, self).__init__(layer, idx, parent)
        self.setupUi(self)

    def config( self ):
        return {}

    def setConfig( self, config ):
        pass


class SIDCWidgetWrapperFactory(QgsEditorWidgetFactory):
    def __init__(self):
        QgsEditorWidgetFactory.__init__(self, 'SIDC code editor')

    def create(self, layer, fieldIdx, editor, parent):
        self.wrapper =  SIDCWidgetWrapper(layer, fieldIdx, editor, parent)
        return self.wrapper

    def configWidget(self, layer, idx, parent ):
        self._configWidget = SIDCWidgetWrapperConfig(layer, idx, parent)
        return self._configWidget
