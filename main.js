const { app, BrowserWindow } = require('electron/main');
const { spawn } = require('child_process');
const path = require('node:path');
const http = require('http');
const kill = require('tree-kill');
const enDev = !app.isPackaged;

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
  startServer();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      stopServer();
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  stopServer();
  if (process.platform !== "darwin") {
    app.quit();
  }
});
