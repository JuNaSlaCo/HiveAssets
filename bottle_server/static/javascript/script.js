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