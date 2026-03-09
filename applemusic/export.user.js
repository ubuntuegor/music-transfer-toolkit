// ==UserScript==
// @name        Apple Music Playlist Export
// @namespace   music-transfer-toolkit
// @match       https://music.apple.com/*
// @grant       GM.registerMenuCommand
// @grant       GM.download
// @grant       GM.xmlhttpRequest
// @version     1.0
// @author      ubuntuegor
// @description Use the userscript menu to export currently opened playlist. Tested on ViolentMonkey.
// ==/UserScript==

async function startExport() {
  const playlistId = getCurrentPlaylistId()

  if (playlistId === null) {
    alert("You don't seem to be on a library playlist page, please try again.")
    return
  }

  const indicator = createIndicator()

  let endpoint = getApiEndpoint(playlistId, 0)
  let total = null
  let count = 0

  const results = [
    ["Title", "Album", "Artist", "IsStreamable"]
  ]

  try {
    updateIndicator(indicator, "Starting export...")

    while (true) {
      const d = await makeApiRequest(endpoint)
      const data = parseResponse(d)

      if (total === null) total = data.total

      for (const track of data.tracks) {
        results.push(
          [track.title || "", normalizeAlbumName(track.album || ""), track.artist || "", track.isStreamable]
        )
        count++
      }

      updateIndicator(indicator, `Exported ${count} out of ${total}`)

      if (data.next) {
        const offsetMatch = data.next.match(/offset=([\d]+)/)
        let offset
        if (offsetMatch !== null) {
          offset = parseInt(offsetMatch[1])
        }
        else {
          offset = 100
          console.warn("assuming offset " + offset)
        }
        endpoint = getApiEndpoint(playlistId, offset)
      }
      else {
        break
      }
    }

    const csv = toCsvDataString(results)
    GM.download(csv, `AppleMusicExport-${playlistId}-${new Date().toLocaleString()}.csv`)

    alert(`Finished exporting ${count} out of ${total} tracks!`)
  }
  catch (e) {
    console.error(e)
    alert(e)
  }
  finally {
    destroyIndicator(indicator)
  }
}

function getCurrentPlaylistId() {
  const path = unsafeWindow.location.pathname
  const result = path.match(/\/library\/playlist\/([^\/]+)/)
  return result !== null ? result[1] : null
}

function getApiEndpoint(playlistId, offset) {
  const params = new URLSearchParams()
  params.append("l", "en-GB")
  params.append("l", "en-US")
  params.append("offset", offset)
  params.append("art[url]", "f")
  params.append("fields[artists]", "name,url")
  params.append("fields[songs]", "artistUrl,url")
  params.append("format[resources]", "map")
  params.append("include", "catalog")
  params.append("include[songs]", "artists")
  params.append("platform", "web")

  return `https://amp-api.music.apple.com/v1/me/library/playlists/${playlistId}/tracks?` + params.toString()
}

async function makeApiRequest(url) {
  const tokenMatch = unsafeWindow.document.cookie.match(/media-user-token=([^;]+);?/)
  const mediaUserToken = tokenMatch !== null ? tokenMatch[1] : null

  if (mediaUserToken === null) {
    throw new Error("media-user-token not found")
  }

  return new Promise((resolve, reject) => {
    GM.xmlhttpRequest({
      url,
      headers: {
        "Alt-Used": "amp-api.music.apple.com",
        // this token is hard-coded in music.apple.com
        "Authorization": "Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IldlYlBsYXlLaWQifQ.eyJpc3MiOiJBTVBXZWJQbGF5IiwiaWF0IjoxNzcyMDYzMTU2LCJleHAiOjE3NzkzMjA3NTYsInJvb3RfaHR0cHNfb3JpZ2luIjpbImFwcGxlLmNvbSJdfQ._dAMwhTgOuEwjx4koR3SR8RXfNU0XRosOrglVesNh5ujz8qK2FWaGSjq53s1YtO9bx67xPNljntmEw9xOCbeOw",
        "media-user-token": mediaUserToken,
        "Origin": "https://music.apple.com",
        "Priority": "u=4",
        "Referer": "https://music.apple.com/",
      },
      onerror: e => {
        reject(e)
      },
      onload: r => {
        try {
          resolve(JSON.parse(r.responseText))
        }
        catch (e) {
          reject(e)
        }
      },
    })
  })
}

function parseResponse(d) {
  const tracks = []

  for (const entry of d["data"]) {
    const song = d["resources"]["library-songs"][entry["id"]]

    const track = {}
    track.title = song["attributes"]["name"]
    track.album = song["attributes"]["albumName"]
    track.artist = song["attributes"]["artistName"]
    track.isStreamable = "playParams" in song["attributes"]

    tracks.push(track)
  }

  const result = { tracks }
  result.total = d["meta"]["total"]
  if ("next" in d) {
    result.next = d["next"]
  }

  return result
}

function normalizeAlbumName(name) {
  return name.replace(/ - Single$/, "").replace(/ - EP$/, "")
}

function createIndicator() {
  const indicator = document.createElement("div")
  indicator.style = "position: absolute; top: 0; left: 0; background-color: var(--pageBG); box-shadow: 0px 2px 5px #333; padding: 10px; z-index: 20000;"
  unsafeWindow.document.body.appendChild(indicator)
  return indicator
}

function updateIndicator(indicator, text) {
  indicator.innerText = text
}

function destroyIndicator(indicator) {
  unsafeWindow.document.body.removeChild(indicator)
}

function makeCsvValue(v) {
  const str = v.toString()
  if (str.match(/[,"\r\n]/)) {
    return '"' + str.replaceAll('"', '""') + '"'
  }
  else {
    return str
  }
}

function toCsvDataString(d) {
  let result = ""
  for (const line of d) {
    for (let i = 0; i < line.length; i++) {
      if (i !== 0) result += ","
      result += makeCsvValue(line[i])
    }
    result += "\n"
  }

  return "data:text/csv," + encodeURIComponent(result)
}

GM.registerMenuCommand("Export playlist", startExport)
