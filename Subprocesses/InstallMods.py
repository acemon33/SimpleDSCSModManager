import os
import shutil

from PyQt5 import QtCore 

from ModFiles.Indexing import generate_mod_index
from ModFiles.PatchGen import generate_patch
from Utils.MBE import mbe_batch_pack


class InstallModsWorkerThread(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    messageLog = QtCore.pyqtSignal(str)
    updateMessageLog = QtCore.pyqtSignal(str)
    lockGui = QtCore.pyqtSignal()
    releaseGui = QtCore.pyqtSignal()
    
    def __init__(self, output_loc, resources_loc, game_resources_loc,  backups_loc,
                 profile_handler, dscstools_handler, parent=None):
        super().__init__(parent)
        self.output_loc = output_loc
        self.resources_loc = resources_loc
        self.game_resources_loc = game_resources_loc
        self.backups_loc = backups_loc
        self.profile_handler = profile_handler
        self.dscstools_handler = dscstools_handler
        
    def run(self):
        try:
            self.lockGui.emit()
            self.messageLog.emit("Preparing to patch mods together...")
            patch_dir = os.path.relpath(os.path.join(self.output_loc, 'patch'))
            dbdsp_dir = os.path.relpath(os.path.join(self.output_loc, 'DSDBP'))
            mvgl_loc = os.path.join(self.output_loc, 'DSDBP.steam.mvgl')
            if os.path.exists(patch_dir):
                shutil.rmtree(patch_dir)
            if os.path.exists(dbdsp_dir):
                shutil.rmtree(dbdsp_dir)
            if os.path.exists(mvgl_loc):
                os.remove(mvgl_loc)
                
            # Do this on mod registry...
            self.messageLog.emit("Indexing mods...")
            indices = []
            for mod in self.profile_handler.get_active_mods():
                modfiles_path = os.path.relpath(os.path.join(mod.path, "modfiles"))
                indices.append(generate_mod_index(modfiles_path, {}))
            self.messageLog.emit(f"Indexed ({len(indices)}) active mods.")
            if len(indices) == 0:
                raise Exception("No mods activated.")
            self.messageLog.emit("Generating patch...")
            generate_patch(indices, patch_dir, self.resources_loc)
            
            # Pack each mbe
            mbe_batch_pack(patch_dir, self.dscstools_handler, self.messageLog.emit, self.updateMessageLog.emit)
            
            self.messageLog.emit("Generating patched MVGL archive (this may take a few minutes)...")
        
            dsdbp_resource_loc = os.path.join(self.resources_loc, 'DSDBP')
            if not os.path.exists(dsdbp_resource_loc):
                self.messageLog.emit("Base DSDBP archive not found, generating...")
                self.dscstools_handler.dump_mvgl('DSDBP', self.game_resources_loc, self.resources_loc)
            shutil.copytree(dsdbp_resource_loc, dbdsp_dir)
            shutil.copytree(patch_dir, dbdsp_dir, dirs_exist_ok=True)
            self.dscstools_handler.pack_mvgl('DSDBP', self.output_loc, self.output_loc, remove_input=False)
            self.dscstools_handler.encrypt_mvgl('DSDBP', self.output_loc, self.output_loc, remove_input=True)
            self.messageLog.emit("Installing patched archive...")
            # Now here's the important bit
            create_backups(self.game_resources_loc, self.backups_loc, self.messageLog.emit)
            shutil.copy2(mvgl_loc, os.path.join(self.game_resources_loc, 'DSDBP.steam.mvgl'))
            
            self.messageLog.emit("Mods successfully installed.")
            
        except Exception as e:
            self.messageLog.emit(f"The following error occured when trying to install modlist: {e}")
            raise e
        finally:
            self.releaseGui.emit()
            self.finished.emit()
            
    
def create_backups(game_resources_loc, backups_loc, logfunc):
    backup_filepath = os.path.join(backups_loc, 'DSDBP.steam.mvgl')
    if not os.path.exists(backup_filepath):
        logfunc("Creating backup...")
        os.mkdir(os.path.split(backup_filepath)[0])
        shutil.copy2(os.path.join(game_resources_loc, 'DSDBP.steam.mvgl'), backup_filepath)