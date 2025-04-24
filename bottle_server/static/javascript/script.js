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
    showNotification("info", "Mise a jour disponible !", 2000);
});
    
window.electronAPI.onNoUpdateAvailable(() => {
    console.log("Aucune mise a jour disponible !");
    showNotification("info", "Aucune mise a jour disponible !", 2000);
});
    
window.electronAPI.onUpdateProgress((event, progress) => {
    console.log(`Progression : ${progress.percent}%`);
    showNotification("info", `Progression : ${int(progress.percent)}%`, 1000);
});
    
window.electronAPI.onUpdateDownloaded(() => {
    console.log("Téléchargement terminé, prêt à redémarrer !");
    showNotification("info", "Téléchargement terminé !", 5000, () => {window.electronAPI.restartApp();}, "Redémarrer maintenant");
});

function showNotification(type, message, duration = 5000, callbutton = null, callbuttonname = null, notifaudio = null) {
    const minDuration = 1000;
    duration = Math.max(duration, minDuration);

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

    if (notifaudio !== null) {
        const notifaudio = document.createElement('audio');
        notifaudio.src = notifaudio;
        notif.appendChild(notifaudio);
        notifaudio.play();
    }
  
    container.appendChild(notif);
  
    setTimeout(() => {
        notif.classList.add("delnotification");
        setTimeout(() => {
            notif.remove();
        }, 500);
    }, duration - 500);
}
window.addEventListener('DOMContentLoaded', () => {
    window.electronAPI.onCheckForUpdate();
});