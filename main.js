const { app, BrowserWindow, ipcMain } = require('electron/main');
const { execSync, spawn } = require('child_process');
const path = require('node:path');
const http = require('http');

const serverPath = path.join(__dirname, "bottle_server");

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
    icon: path.join(__dirname, 'bottle_server/static/icons/HiveAssets.png'),
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
  server = spawn("python", ["server.py"], { cwd: serverPath, detached: true, stdio: "ignore" });
  server.unref();
}

function stopServer() {
  if (server) {
    try {
      if (process.platform === "win32") {
        execSync(`taskkill /PID ${server.pid} /T /F`);
      } else {
        process.kill(-server.pid, "SIGTERM");
      }
    } catch (error) {
      console.error("Erreur lors de la fermeture du serveur:", error);
    }
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
  if (process.platform !== "darwin") {
    stopServer();
    app.quit();
  }
});
