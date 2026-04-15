import urllib.request
import re
import os

SOURCE_URL = "https://raw.githubusercontent.com/36mafia/Pluto-TV-Playlists-2026/refs/heads/main/output/plutotv_us.m3u8"

# Maps Pluto channel hex ID -> desired channel number
# Channels missing from the feed (weathernation-2, cars-1) will be skipped automatically
CHANNEL_MAP = {
    "5d2cb7ac552e3773bc48982e": "202",  # weathernation-2
    "640a68880e884c0009979cc2": "203",  # fox-weather
    "55b179af994403942f3061d6": "212",  # newsmax2
    "5e7cf6c7b156d500078c5f44": "213",  # oan-plus
    "65d92a8c8b24c80008e285c0": "214",  # bbc-news
    "656535fc2c46f30008870fae": "251",  # bbc-earth
    "5f21ea08007a49000762d349": "252",  # smithsonian-channel-selects
    "640a64bd73e013000893d4e0": "254",  # pbs-nature
    "66df8a29b25d2b0008fc5fe0": "260",  # love-nature
    "5812bd9f249444e05d09cc4e": "261",  # naturescape
    "563a970aa1a1f7fe7c9daad7": "263",  # pluto-tv-science
    "66e0b4866ad04d0008fff4d8": "264",  # mythbusters
    "65775d29dfed030008cb3db2": "266",  # modern-marvels-presented-by-history
    "5a4d35dfa5c02e717a234f86": "267",  # pluto-tv-history
    "6887aaf4e3703b7d42b71a1e": "269",  # storage-wars
    "5bb3fea0f711fd76340eebff": "270",  # pluto-tv-military
    "65c69bf23ef47d0008583967": "271",  # tough-jobs
    "5cabdf1437b88b26947346b2": "272",  # pluto-tv-backcountry
    "5873fc21cad696fb37aa9054": "273",  # live-music
    "68939e206727ec919bb39061": "301",  # hogans-heroes
    "60f75178e7f8aa0007e9c259": "302",  # the-andy-griffith-show
    "5d81607ab737153ea3c1c80e": "303",  # the-addams-family
    "5f36d726234ce10007784f2a": "304",  # the-bob-ross-channel
    "5e8df4bc16e34700077e77d3": "305",  # western-tv
    "60f75771dfc72a00071fd0e0": "306",  # gunsmoke
    "68e9913c4a666b9054849832": "307",  # bonanza
    "664e640a0120f40008be4582": "308",  # wild-wild-west
    "634f307c7a068e00072c9982": "309",  # rawhide
    "5e825550e758c700077b0aef": "310",  # the-rifleman
    "61f33318210549000806a530": "311",  # classic-movie-westerns-ptv1
    "67352ed93a61d4000881f9fa": "312",  # the-twilight-zone-ptv
    "5ce4475cd43850831ca91ce7": "313",  # doctor-who-classic
    "6549306c83595c000815a696": "350",  # nbc-sports-now
    "5a74b8e1e22a61737979c6bf": "356",  # fox-sports
    "6792c30abc03978b9b8bb832": "377",  # the-nba-channel
    "63a0e33a45264d000850ed7e": "382",  # golazo-network
    "65ea8b928145cb0008509426": "383",  # uefa-champions-league
    "681109b688b9d85d0938c6ba": "387",  # tennischannel-2
    "5616f9c0ada51f8004c4b091": "397",  # world-poker-tour
    "5fc54366b04b2300072e31af": "398",  # pokergo
    "5c12ba66eae03059cbdc77f2": "454",  # cars-1
    "5f4d8594eb979c0007706de7": "455",  # pluto-tv-crime-movies
    "5f4d86f519358a00072b978e": "456",  # 90s-throwback
    "5ca525b650be2571e3943c63": "457",  # 80s-rewind
    "5f4d878d3d19b30007d2e782": "458",  # 70s-cinema
}

def fetch_playlist(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return r.read().decode("utf-8")

def filter_playlist(content):
    lines = content.splitlines()
    output = ["#EXTM3U"]
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF"):
            # Extract tvg-id to check against our map
            m = re.search(r'tvg-id="([^"]+)"', line)
            url_line = lines[i + 1] if i + 1 < len(lines) else ""
            if m and m.group(1) in CHANNEL_MAP:
                hex_id = m.group(1)
                ch_num = CHANNEL_MAP[hex_id]
                # Inject/replace tvg-chno with our desired channel number
                new_line = re.sub(r'tvg-chno="[^"]*"', f'tvg-chno="{ch_num}"', line)
                if 'tvg-chno=' not in new_line:
                    new_line = new_line.replace("#EXTINF:-1 ", f'#EXTINF:-1 tvg-chno="{ch_num}" ')
                output.append(new_line)
                output.append(url_line)
            i += 2
        else:
            i += 1
    return "\n".join(output) + "\n"

if __name__ == "__main__":
    print(f"Fetching {SOURCE_URL}...")
    content = fetch_playlist(SOURCE_URL)
    filtered = filter_playlist(content)
    
    os.makedirs("PlutoTV", exist_ok=True)
    out_path = "PlutoTV/my_channels.m3u8"
    with open(out_path, "w") as f:
        f.write(filtered)
    
    channel_count = filtered.count("#EXTINF")
    print(f"Done. {channel_count} channels written to {out_path}")
