const settings = () => {
    const s = document.getElementById("settings");
    s.classList.toggle("invisible");
    const e = document.getElementById("doc");
    e.classList.toggle("doc2");
    const a = document.getElementById("filtres");
    a.classList.toggle("filtres2");
}
function reloadiframe(url){
    const iframe = document.getElementById("viewer");
    iframe.src = url;
}
function openfileonsystem(url){
    open(url)
}
let oldaudio = '';
function playaudio(url){
    const player = document.getElementById('main-audio');
    if (oldaudio !== url) {
        player.src = url;
        player.play();
        oldaudio = url;
    } else {
        if (player.paused) {
            player.play();
        } else {
            player.pause();
        }
    }
}
function dragFile(file) {
    if (window.electronAPI && window.electronAPI.startFileDrag) {
        window.electronAPI.startFileDrag(file)
    } else {
        console.warn("electronAPI.startFileDrag non trouvé")
    }
}
window.addEventListener('message', (event) => {
    if (event.data.action === 'open-folder-dialog') {
        window.electronAPI.openFolderDialog();
    }
    if (event.data.action === 'restart-app') {
        window.electronAPI.restartApp();
    }
    if (event.data.action === 'check-for-update') {
        window.electronAPI.onCheckForUpdate();
    }
  });

window.electronAPI.onFolderSelected((repPath) => {
    console.info(repPath)
    const iframe = document.getElementById('settings-page');
    if (iframe && iframe.contentWindow) {
        iframe.contentWindow.postMessage({ action: 'folder-selected', path: repPath }, '*');
    }
});
function refreshPreview(img) {
    setTimeout(() => {
        img.src = img.src;
    }, 1500);
}
window.electronAPI.onUpdateAvailable(() => {
    console.log("Update disponible !");
    showNotification("Mise a jour disponible !", 7500);
});
    
window.electronAPI.onNoUpdateAvailable(() => {
    console.log("Aucune mise a jour disponible !");
    showNotification("Aucune mise a jour disponible !");
});
    
window.electronAPI.onUpdateProgress((event, progress) => {
    console.log(`Progression : ${progress.percent}%`);
    showNotification(`Progression : ${progress.percent}%`, 7500);
});
    
window.electronAPI.onUpdateDownloaded(() => {
    console.log("Téléchargement terminé, prêt à redémarrer !");
    showNotification("Téléchargement terminé, prêt à redémarrer !", 7500, () => {window.electronAPI.restartApp();}, "Redémarrer");
});

function showNotification(message, duration = 7500, callbutton = null, callbuttonname = null) {
    const container = document.getElementById('notifications-container');
  
    const notif = document.createElement('div');
    notif.className = 'notification';

    const msg = document.createElement('span');
    msg.innerText = message;
    notif.appendChild(msg);

    if (callbutton !== null) {
        const notifbtn = document.createElement('button');
        notifbtn.className = 'notification-button';
        notifbtn.innerText = callbuttonname;
        notifbtn.onclick = callbutton;
        notif.appendChild(notifbtn);
    }
  
    container.appendChild(notif);
  
    setTimeout(() => {
      notif.remove();
    }, duration);
}
window.addEventListener('DOMContentLoaded', () => {
    window.electronAPI.onCheckForUpdate();
    console.log("test")
});