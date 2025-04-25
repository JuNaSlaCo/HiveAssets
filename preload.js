const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  startFileDrag: (file) => ipcRenderer.send('drag-file', { file }),
  onServerReady: (callback) => ipcRenderer.on('pret', callback),
  openFolderDialog: () => ipcRenderer.invoke('openfolder'),
  onFolderSelected: (callback) => ipcRenderer.on('selectfolder', (event, path) => callback(path)),
  onUpdateAvailable: (callback) => ipcRenderer.on("update-available", callback),
  onNoUpdateAvailable: (callback) => ipcRenderer.on("update-not-available", callback),
  onUpdateProgress: (callback) => ipcRenderer.on("download-progress", callback),
  onUpdateDownloaded: (callback) => ipcRenderer.on("update-downloaded", callback),
  onCheckForUpdate: () => ipcRenderer.send("check-for-update"),
  onUpdaterError: (callback) => ipcRenderer.on("updater-error", callback),
  restartApp: () => ipcRenderer.send('restart-app')
})
