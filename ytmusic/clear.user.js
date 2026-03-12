// ==UserScript==
// @name        YouTube Music Clear Likes
// @namespace   music-transfer-toolkit
// @match       https://music.youtube.com/*
// @grant       GM.registerMenuCommand
// @version     1.0
// @author      -
// @description Use the userscript menu to clear the Liked Music playlist (it has to be open). Tested on ViolentMonkey.
// ==/UserScript==

const LIKE_BUTTONS_SELECTOR = "ytmusic-like-button-renderer[like-status=LIKE] .like button"

GM.registerMenuCommand("Start clearing", () => {
    const buttons = Array.from(unsafeWindow.document.querySelectorAll(LIKE_BUTTONS_SELECTOR))

    function loop() {
        if (buttons.length > 0) {
            buttons.shift().click()
            setTimeout(loop, 400)
        }
    }

    loop()
})
