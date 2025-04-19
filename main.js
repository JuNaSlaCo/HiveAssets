const { app, BrowserWindow, ipcMain, nativeImage, dialog } = require('electron/main');
const { spawn } = require('child_process');
const { autoUpdater } = require('electron-updater');
const path = require('node:path');
const http = require('http');
const kill = require('tree-kill');
const log = require("electron-log");
const enDev = !app.isPackaged;
let ffmpegPath = require('ffmpeg-static');

if (ffmpegPath.includes('app.asar')) {
  ffmpegPath = ffmpegPath.replace('app.asar', 'app.asar.unpacked');
}

const serverPath = enDev
    ? path.join(__dirname, 'bottle_server', 'dist', 'server.exe')
    : path.join(process.resourcesPath, 'bottle_server', 'server.exe');

const defaulticon = enDev
    ? path.join(__dirname, 'build_assets', 'icon.png')
    : path.join(process.resourcesPath, 'icon.png');

let server;
let win;
let serverLoaded = false;
let finishupdate = true;

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
    console.warn("Erreur de décodage du repertoire :", quotePath);
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
    console.log(`Server exited with code: ${code}`);
    log.debug(`Server exited with code: ${code}`);
  });

  server.on('error', (err) => {
    console.error(`Error starting server: ${err.message}`);
    log.error(`Error starting server: ${err.message}`);
  });
}

function stopServer() {
  if (server) {
    console.log("Arrêt du serveur");
    log.debug("Arrêt du serveur");
    kill(server.pid, 'SIGTERM', (err) => {
      if (err) {
        console.error("Erreur de l'arrêt du serveur :", err);
        log.error("Erreur de l'arrêt du serveur :", err);
      } else {
        console.log("Serveur arrêté.");
        log.debug("Serveur arrêté.");
      }
      server = null;
    });
  } else {
    console.log("Le serveur n'est pas démarré.");
  }
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
          console.log("Serveur pas encore prêt...");
          log.debug("Serveur pas encore prêt...");
      });
  }, 1000);
}

app.whenReady().then(() => {
  autoUpdater.checkForUpdatesAndNotify();
  startServer();
  createWindow();

  ipcMain.on('drag-file', (event, { file }) => {
    const win = BrowserWindow.getFocusedWindow()
    if (!win) return

    const decodePath = unquotePath(file);
    console.log(decodePath)
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
    })
  })

  ipcMain.handle('openfolder', async (event) => {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory']
    });
  
    if (!result.canceled && result.filePaths.length > 0) {
      result.filePaths[0] = Buffer.from(result.filePaths[0], 'utf-8').toString('base64');
      event.sender.send('selectfolder', result.filePaths[0]);
      console.info(result);
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
  console.log("Update available !");
  log.debug("Update available !");
  finishupdate = false;
})

autoUpdater.on("checking-for-update", () => {
  console.log("checking for update");
  log.debug("checking for update");
})

autoUpdater.on("download-progress", (progressTrack) => {
  console.log(progressTrack);
  log.debug(progressTrack);
})

autoUpdater.on("error", (err) => {
  console.log("Erreur de l'auto-updater : ", err);
  log.debug("Erreur de l'auto-updater : ", err);
})

autoUpdater.on("update-downloaded", () => {
  finishupdate = true
  console.log("Download finish !");
  log.debug("Download finish !");
})

app.on("window-all-closed", () => {
  stopServer();
  if (finishupdate){
    if (process.platform !== "darwin") {
      app.quit();
    }
  } else {
    setInterval(() => {
      if (finishupdate){
        app.quit();
      }
    }, 5000);
  }
});
