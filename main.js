const { app, BrowserWindow, autoUpdater } = require('electron/main');
const { spawn } = require('child_process');
const path = require('node:path');
const http = require('http');
const kill = require('tree-kill');
const enDev = !app.isPackaged;

const updateserver = "https://update.electronjs.org";
const repo = "JuNaSlaCo/HiveAssets";
const feedURL = `${updateserver}/${repo}/${process.platform}-${process.arch}/${app.getVersion()}`;

autoUpdater.setFeedURL({ url: feedURL });

const serverPath = enDev
    ? path.join(__dirname, 'bottle_server', 'dist', 'server.exe')
    : path.join(process.resourcesPath, 'bottle_server', 'server.exe');

let server;
let win;
let serverLoaded = false;

function createWindow() {
  win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
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

function startServer() {
  server = spawn(serverPath, {
      stdio: 'ignore'
  });

  server.on('exit', (code) => {
    console.log(`Server exited with code: ${code}`);
  });

  server.on('error', (err) => {
    console.error(`Error starting server: ${err.message}`);
  });
}

function stopServer() {
  if (server) {
    console.log("Arrêt du serveur");
    kill(server.pid, 'SIGTERM', (err) => {
      if (err) {
        console.error("Erreur de l'arrêt du serveur :", err);
      } else {
        console.log("Serveur arrêté.");
      }
      server = null;
    });
  } else {
    console.log("Le serveur n'est pas démarrer.");
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
      });
  }, 1000);
}

app.whenReady().then(() => {
  autoUpdater.checkForUpdates
  startServer();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      stopServer();
      createWindow();
    }
  });
});

autoUpdater.on("update-available", () => {
  dialog.showMessageBox({
    type: "info",
    title: "Mise à jour disponible !",
    message: "Une nouvelle version est disponible ! Téléchargement en cours...",
  });
});

autoUpdater.on("update-downloaded", () => {
  dialog.showMessageBox({
    type: "info",
    title: "Mise à jour prête",
    message: "Redémarrer l'application pour installer la mise a jour.",
    buttons: ["Oui", "Plus tard"],
  }).then((result) => {
    if (result.response === 0) {
      autoUpdater.quitAndInstall();
    }
  });
});

app.on("window-all-closed", () => {
  stopServer();
  if (process.platform !== "darwin") {
    app.quit();
  }
});
