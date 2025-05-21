// app/static/js/index.js

document.addEventListener('DOMContentLoaded', function() {
    if (window.flashedMessages && Array.isArray(window.flashedMessages)) {
        window.flashedMessages.forEach(msg => {
            alert(msg.text);
        });
        window.flashedMessages = [];
    }
});