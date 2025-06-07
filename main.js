const { app, BrowserWindow, ipcMain, nativeImage, dialog } = require('electron/main');
const { spawn } = require('child_process');
const { autoUpdater } = require('electron-updater');
const path = require('node:path');
const http = require('http');
const kill = require('tree-kill');
const log = require("electron-log");
const os = require('os');
let ffmpegPath = require('ffmpeg-static');
const enDev = !app.isPackaged;
const InstLock = app.requestSingleInstanceLock();
const isWin = os.platform() === 'win32';
let serverPath, defaulticon;

if (!InstLock) {
  app.quit()
} else {
  app.on('second-instance', (event, commandLine, workingDirectory) => {
    if (win) {
      if (win.isMinimized()) {
        win.restore();
      }
      win.focus();
    }
  });

const binaryName = isWin ? 'HASRV.exe' : 'HASRV';

if (ffmpegPath.includes('app.asar')) {
  ffmpegPath = ffmpegPath.replace('app.asar', 'app.asar.unpacked');
};
if (enDev) {
  console.log("🛠 Mode dev détecté");
  console.log("✔️ Path serveur Python :", serverPath);
  serverPath = path.join(__dirname, 'bottle_server', 'dist', isWin ? 'win' : os.platform(), binaryName);
  defaulticon = path.join(__dirname, 'build_assets', 'icon.png');
} else {
  serverPath = path.join(process.resourcesPath, 'bottle_server', binaryName);
  defaulticon = path.join(process.resourcesPath, 'icon.png');
}

let server;
let win;
let serverLoaded = false;
let installupdate = false;

function createWindow() {
  win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    autoHideMenuBar: true
  });

  win.webContents.session.clearCache();
  win.webContents.session.clearStorageData();
  win.maximize();
  win.loadFile('loader.html');
  setInterval(() => {
    if (!serverLoaded) {
      checkServerReady();
    }
  }, 3000);
}

const unquotePath = (quotePath) => {
  try {
    return Buffer.from(quotePath, 'base64').toString('utf-8');
  } catch (e) {
    log.warn("Erreur de décodage du repertoire :", quotePath);
    return quotePath;
  }
};

function startServer() {
  server = spawn(serverPath, {
      stdio: 'ignore',
      env: {
        ...process.env,
        FFMPEG_PATH: ffmpegPath
      }
  });

  server.on('exit', (code) => {
    log.debug(`Server exited with code: ${code}`);
  });

  server.on('error', (err) => {
    log.error(`Error starting server: ${err.message}`);
  });
}

function stopServer() {
  if (server) {
    log.debug("Arrêt du serveur");
    kill(server.pid, 'SIGTERM', (err) => {
      if (err) {
        log.error("Erreur de l'arrêt du serveur :", err);
      } else {
        log.debug("Serveur arrêté.");
      }
      server = null;
    });
  } else {
    console.log("Le serveur n'est pas démarré.");
  };
}

function checkServerReady() {
  const interval = setInterval(() => {
      http.get("http://localhost:5069/ping", (res) => {
          if (res.statusCode === 200 && !serverLoaded) {
              clearInterval(interval);

              win.webContents.send("pret");

              setTimeout(() => {
                  win.loadURL("http://localhost:5069");
                  serverLoaded = true;
              }, 1000);
          }
      }).on("error", () => {
          log.debug("Serveur pas encore prêt...");
      });
  }, 1000);
}

app.whenReady().then(() => {
  startServer();
  createWindow();

  ipcMain.on('drag-file', (event, { file }) => {
    const win = BrowserWindow.getFocusedWindow();
    if (!win) return

    const decodePath = unquotePath(file);
    log.debug(decodePath);
    const ext = path.extname(decodePath);
    let icon;

    if (ext === ".png") {
      icon = nativeImage.createFromPath(decodePath).resize({
        width: 64,
        height: 64
      });
    } else {
      icon = nativeImage.createFromPath(defaulticon).resize({
        width: 64,
        height: 64
      });
    }

    win.webContents.startDrag({
      file: decodePath,
      icon: icon
    });
  })

  ipcMain.handle('openfolder', async (event) => {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory']
    });
  
    if (!result.canceled && result.filePaths.length > 0) {
      result.filePaths[0] = Buffer.from(result.filePaths[0], 'utf-8').toString('base64');
      event.sender.send('selectfolder', result.filePaths[0]);
      log.debug(result);
    } else {
      event.sender.send('selectfolder', null);
    }
  });    

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      stopServer();
      createWindow();
    }
  });
});

autoUpdater.on("update-available", () => {
  win.webContents.send("update-available");
  log.debug("Update available !");
})

autoUpdater.on("update-not-available", () => {
  win.webContents.send("update-not-available");
  log.debug("No update available.");
});

autoUpdater.on("checking-for-update", () => {
  log.debug("checking for update");
})

autoUpdater.on("download-progress", (progressTrack) => {
  win.webContents.send("download-progress", progressTrack);
  log.debug(progressTrack);
})

autoUpdater.on("error", (err) => {
  win.webContents.send("updater-error", err);
  log.debug("Erreur de l'auto-updater : ", err);
})

autoUpdater.on("update-downloaded", () => {
  win.webContents.send("update-downloaded");
  installupdate = true;
  log.debug("Download finish !");
})

ipcMain.on('restart-app', () => {
  stopServer();
  autoUpdater.quitAndInstall();
});

ipcMain.on('check-for-update', () => {
  autoUpdater.checkForUpdates();
});

app.on("window-all-closed", () => {
  stopServer();
  if (installupdate){
    autoUpdater.quitAndInstall();
  } else {
    if (process.platform !== "darwin") {
      app.quit();
    };
  };
});
}