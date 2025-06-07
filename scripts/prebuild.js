const fs = require("fs");
const path = require("path");
const os = require("os");

const platform = os.platform();
const isWin = platform === "win32";
const isMac = platform === "darwin";
const distDir = isWin ? "win" : isMac ? "darwin" : "linux";
const ext = isWin ? ".exe" : "";

const source = path.join("bottle_server", "dist", distDir, "HASRV" + ext);
const dest = path.join("bottle_server", "HASRV" + ext);

if (!fs.existsSync(source)) {
  console.error("Erreur : binaire serveur non trouvé :", source);
  process.exit(1);
}

fs.copyFileSync(source, dest);
console.log(`Binaire serveur copié : ${source} -> ${dest}`);