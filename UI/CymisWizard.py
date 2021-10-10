from PyQt5 import QtCore, QtWidgets

from ModFiles.CymisParser import CymisInstaller


class CymisWizard(QtWidgets.QWizard):
    def __init__(self, filepath, log, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        
        self.installer = CymisInstaller.init_from_script(filepath, log)
        self.log = self.installer.log
        
        self.pages = [CymisWizardPage(page_source, self.log) for page_source in self.installer.wizard_pages]
        for page in self.pages:    
            self.addPage(page)
        
            
        self.currentCymisPageIndex = 0
        
        self.setWindowTitle("Cymis Installer Wizard")
        self.resize(640,480)
        # This is neat, but I don't know how to catch exceptions from it!
        # self.button(QtWidgets.QWizard.FinishButton).clicked.connect(self.launch_installation)
    
    def launch_installation(self):
        # Should hook into this to provide GUI logging functions
        self.installer.install_mod()


###################
# FLAG TYPE VIEWS #
###################
class FlagView(QtWidgets.QCheckBox):
    def __init__(self, flag_data, log, parent=None):
        super().__init__(flag_data.description, parent)
        self.log = log
        
        self.flag_data = flag_data
        
        self.setCheckState(QtCore.Qt.Checked if flag_data.value else QtCore.Qt.Unchecked)
        self.stateChanged.connect(self.flipFlag)
        
    def flipFlag(self):
        if self.log is not None:
            self.log(f"Flipping {self.flag_data.name} to {self.isChecked()}.")
        self.flag_data.value = self.isChecked()

class ChooseOneView(QtWidgets.QWidget):
    def __init__(self, flag_data, log, parent=None):
        super().__init__(parent)
        
        self.flag_data = flag_data
        self.log = log
        self.buttongroup = QtWidgets.QButtonGroup()
        self.buttongroup.setExclusive(True)
        
        self.layout = QtWidgets.QVBoxLayout()
        
        for flagname, flag in self.flag_data.flags.items():
            radiobutton = QtWidgets.QRadioButton(flag.description)
            radiobutton.setChecked(flag.value)
            radiobutton.toggled.connect(self.generate_togglefunc(flagname, radiobutton))
            self.buttongroup.addButton(radiobutton)
            self.layout.addWidget(radiobutton)
            
        self.setLayout(self.layout)
        
    def flipFlag(self, flagname, sender):
        if self.log is not None:
            self.log(f"Flipping {flagname} to {sender.isChecked()}.")
        self.flag_data.flags[flagname].value = sender.isChecked()
     
    def generate_togglefunc(self, flagname, radiobutton):
        return lambda: self.flipFlag(flagname, radiobutton)
        
flagviews = {'Flag': FlagView, 'ChooseOne': ChooseOneView}
        
class CymisWizardPage(QtWidgets.QWizardPage):
    def __init__(self, installer_page, log, parent=None):
        super().__init__(parent)
        self.page_data = installer_page
        self.log = log
        self.lay_out()
        
    def lay_out(self):
        layout = QtWidgets.QVBoxLayout()
        
        self.title = QtWidgets.QLabel(self.page_data.title)
        self.title.setWordWrap(True)
        self.description = QtWidgets.QLabel(self.page_data.contents)
        self.description.setWordWrap(True)
        layout.addWidget(self.title)
        layout.addWidget(self.description)
        
        for flag_data in self.page_data.flags:
            flag_view_widget = flagviews.get(flag_data.type)
            if flag_view_widget is not None:   
                layout.addWidget(flag_view_widget(flag_data, self.log))
        
        self.setLayout(layout)
