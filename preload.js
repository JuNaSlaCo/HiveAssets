const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  startFileDrag: (file) => ipcRenderer.send('drag-file', { file }),
  onServerReady: (callback) => ipcRenderer.on('pret', callback)
})