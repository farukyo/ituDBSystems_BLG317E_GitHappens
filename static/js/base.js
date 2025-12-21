const sidebar = document.getElementById("sidebar");
const mainContent = document.getElementById("main-content");
const openBtn = document.getElementById("openMenuBtn");
const closeBtn = document.querySelector(".sidebar .closebtn");

const sidebarWidth = "250px";


const beeLoadingPopup = document.getElementById("beeLoadingPopup");


function showBeeLoading() {
    if (beeLoadingPopup) {
        beeLoadingPopup.classList.add("show");
    }
}


function hideBeeLoading() {
    if (beeLoadingPopup) {
        beeLoadingPopup.classList.remove("show");
    }
}


function toggleNav() {
    
    if (sidebar.style.width === sidebarWidth) {
        
        sidebar.style.width = "0";
        
        return false; 
    } else {
        
        sidebar.style.width = sidebarWidth;
        
        return true; 
    }
}



document.addEventListener('DOMContentLoaded', () => {

    
    if (openBtn) {
        openBtn.addEventListener('click', toggleNav);
    }

    
    if (closeBtn) {
        closeBtn.addEventListener('click', toggleNav);
        
    }

   
    document.addEventListener('click', function (event) {
        
        if (sidebar.style.width === sidebarWidth) {

            
            if (!sidebar.contains(event.target) && !openBtn.contains(event.target)) {
                
                toggleNav();
            }
        }
    });


    const dbPages = ['/movies', '/series', '/episodes', '/celebrities', '/recommend', '/quiz'];

    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');

            if (href && dbPages.some(page => href.includes(page))) {
                
                if (!href.startsWith('#') && !href.startsWith('javascript:')) {
                    showBeeLoading();
                }
            }
        });
    });


    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function () {
            showBeeLoading();
        });
    });


    hideBeeLoading();
});


window.addEventListener('pageshow', function (event) {
    hideBeeLoading();
});


window.addEventListener('pagehide', function (event) {
    // Sayfa kapanırken popup'ı sıfırla
});


window.addEventListener('load', function () {
    hideBeeLoading();
});