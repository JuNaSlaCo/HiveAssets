const { app, BrowserWindow } = require('electron/main')
const { exec, execSync, spawn } = require('child_process');
const path = require('node:path');
const serverPath = path.join(__dirname, "bottle_server");

let server;

function createWindow () {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
        nodeIntegration: true
    },
    autoHideMenuBar: true
  })
  win.maximize();
  win.loadFile('loader.html');
  setTimeout(() => {
    win.loadURL('http://localhost:5069');
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

app.whenReady().then(() => {
    startServer();
    createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        stopServer();
        createWindow();
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    stopServer();
    app.quit();
  }
})