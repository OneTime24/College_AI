from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

LOCATIONS = {
    "main gate": {
        "name": "Main Gate",
        "building": "Main Entrance",
        "floor": "Ground Floor",
        "description": "The main entrance of the college.",
        "x": 100,
        "y": 400
    },
    "admin block": {
        "name": "Admin Block",
        "building": "Administration Block",
        "floor": "Ground Floor",
        "description": "Administration offices, principal office and reception.",
        "x": 300,
        "y": 250
    },
    "computer lab": {
        "name": "Computer Lab",
        "building": "CS Block",
        "floor": "2nd Floor",
        "description": "Computer science laboratory.",
        "x": 650,
        "y": 180
    },
    "cs department": {
        "name": "CS Department",
        "building": "CS Block",
        "floor": "2nd Floor",
        "description": "Computer Science department offices.",
        "x": 650,
        "y": 300
    },
    "library": {
        "name": "Library",
        "building": "Academic Block",
        "floor": "1st Floor",
        "description": "College library and study area.",
        "x": 430,
        "y": 450
    },
    "cafeteria": {
        "name": "Cafeteria",
        "building": "Student Center",
        "floor": "Ground Floor",
        "description": "College cafeteria and student seating area.",
        "x": 700,
        "y": 480
    },
    "physics lab": {
        "name": "Physics Lab",
        "building": "Science Block",
        "floor": "1st Floor",
        "description": "Physics laboratory.",
        "x": 220,
        "y": 520
    },
    "lecture hall": {
        "name": "Lecture Hall",
        "building": "Academic Block",
        "floor": "Ground Floor",
        "description": "Large lecture hall for classes and events.",
        "x": 450,
        "y": 170
    },
    "principal office": {
        "name": "Principal Office",
        "building": "Admin Block",
        "floor": "1st Floor",
        "description": "Office of the college principal.",
        "x": 320,
        "y": 180
    },
    "parking": {
        "name": "Parking",
        "building": "Parking Area",
        "floor": "Ground",
        "description": "College parking area.",
        "x": 80,
        "y": 180
    }
}

ALIASES = {
    "cs lab": "computer lab",
    "computer science lab": "computer lab",
    "computing lab": "computer lab",
    "computer department": "cs department",
    "computer science department": "cs department",
    "library": "library",
    "canteen": "cafeteria",
    "food": "cafeteria",
    "principal": "principal office",
    "entrance": "main gate",
    "gate": "main gate",
    "car parking": "parking",
    "parking area": "parking"
}


def normalize(text):
    return " ".join(text.lower().strip().split())


def find_location(query):
    query = normalize(query)

    if query in LOCATIONS:
        return query

    if query in ALIASES:
        return ALIASES[query]

    for key in LOCATIONS:
        if key in query:
            return key

    for alias, target in ALIASES.items():
        if alias in query:
            return target

    return None


def calculate_route(start, destination):
    if not start:
        return [
            destination
        ]

    return [start, destination]


def process_query(query):
    q = normalize(query)

    destination = find_location(q)

    if not destination:
        return {
            "success": False,
            "message": (
                "I couldn't find that location. "
                "Try asking for the library, computer lab, "
                "CS department, cafeteria, admin block or main gate."
            )
        }

    location = LOCATIONS[destination]

    route = calculate_route(None, destination)

    if any(word in q for word in [
        "where is",
        "where's",
        "location of",
        "find",
        "take me",
        "how do i get",
        "how can i get",
        "directions"
    ]):
        message = (
            f"{location['name']} is in the {location['building']}, "
            f"{location['floor']}. {location['description']}"
        )
    else:
        message = (
            f"{location['name']} is in the {location['building']}, "
            f"{location['floor']}."
        )

    return {
        "success": True,
        "message": message,
        "location": destination,
        "data": location,
        "route": route
    }


HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>AI Campus Navigator</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #0b0f14;
    color: #e8edf3;
    font-family: Arial, Helvetica, sans-serif;
}

header {
    height: 70px;
    border-bottom: 1px solid #222a33;
    display: flex;
    align-items: center;
    padding: 0 30px;
    background: #0d1218;
}

.logo {
    font-size: 21px;
    font-weight: bold;
}

.logo span {
    color: #4da3ff;
}

.status {
    margin-left: auto;
    font-size: 13px;
    color: #7ee787;
}

.container {
    display: grid;
    grid-template-columns: 390px 1fr;
    height: calc(100vh - 70px);
}

.sidebar {
    border-right: 1px solid #222a33;
    padding: 25px;
    background: #0d1218;
}

.title {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 8px;
}

.subtitle {
    color: #7f8b98;
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 25px;
}

.search {
    display: flex;
    gap: 8px;
}

input {
    flex: 1;
    background: #151c24;
    border: 1px solid #2b3541;
    color: white;
    padding: 14px;
    border-radius: 8px;
    outline: none;
}

input:focus {
    border-color: #4da3ff;
}

button {
    border: none;
    border-radius: 8px;
    padding: 12px 15px;
    cursor: pointer;
    font-weight: bold;
}

.ask {
    background: #2563eb;
    color: white;
}

.mic {
    background: #1b2530;
    color: white;
}

.mic.active {
    background: #dc2626;
}

.examples {
    margin-top: 25px;
}

.examples-title {
    color: #7f8b98;
    font-size: 12px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.example {
    background: #131a22;
    border: 1px solid #202a35;
    padding: 11px;
    border-radius: 7px;
    margin-bottom: 7px;
    cursor: pointer;
    font-size: 13px;
}

.example:hover {
    border-color: #3d8df5;
}

.response {
    margin-top: 25px;
    background: #121922;
    border: 1px solid #202a35;
    border-radius: 10px;
    padding: 18px;
}

.response-title {
    color: #7f8b98;
    font-size: 12px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.response-text {
    line-height: 1.5;
}

.location-card {
    margin-top: 15px;
    padding: 15px;
    background: #17202a;
    border-radius: 8px;
    display: none;
}

.location-name {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 8px;
}

.location-info {
    color: #9ca8b5;
    font-size: 13px;
    line-height: 1.6;
}

.map-container {
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
    background-size: 40px 40px;
}

.map-header {
    position: absolute;
    top: 20px;
    left: 25px;
    z-index: 10;
}

.map-title {
    font-size: 18px;
    font-weight: bold;
}

.map-subtitle {
    color: #788594;
    font-size: 12px;
    margin-top: 4px;
}

svg {
    width: 100%;
    height: 100%;
}

.building {
    fill: #18212b;
    stroke: #344352;
    stroke-width: 2;
}

.building:hover {
    fill: #202c38;
}

.road {
    stroke: #27313b;
    stroke-width: 25;
    stroke-linecap: round;
}

.road-line {
    stroke: #3b4651;
    stroke-width: 2;
    stroke-dasharray: 10 10;
}

.location-dot {
    fill: #4da3ff;
    stroke: #071019;
    stroke-width: 3;
    cursor: pointer;
}

.location-dot.active {
    fill: #22c55e;
    r: 11;
}

.location-label {
    fill: #d9e2eb;
    font-size: 13px;
    pointer-events: none;
}

.route {
    stroke: #22c55e;
    stroke-width: 5;
    stroke-linecap: round;
    stroke-dasharray: 12 8;
    fill: none;
    display: none;
}

.legend {
    position: absolute;
    right: 25px;
    bottom: 25px;
    background: #101720;
    border: 1px solid #293541;
    padding: 12px 15px;
    border-radius: 8px;
    font-size: 12px;
}

.legend-item {
    margin: 5px 0;
}

.dot-blue {
    display: inline-block;
    width: 9px;
    height: 9px;
    background: #4da3ff;
    border-radius: 50%;
    margin-right: 6px;
}

.dot-green {
    display: inline-block;
    width: 9px;
    height: 9px;
    background: #22c55e;
    border-radius: 50%;
    margin-right: 6px;
}

@media(max-width: 900px) {
    .container {
        grid-template-columns: 1fr;
        height: auto;
    }

    .sidebar {
        border-right: none;
        border-bottom: 1px solid #222a33;
    }

    .map-container {
        height: 600px;
    }
}

</style>
</head>

<body>

<header>
    <div class="logo">
        AI <span>Campus Navigator</span>
    </div>

    <div class="status">
        ● AI SYSTEM ONLINE
    </div>
</header>

<div class="container">

    <aside class="sidebar">

        <div class="title">
            Where do you want to go?
        </div>

        <div class="subtitle">
            Ask the campus AI for directions, rooms,
            departments, laboratories and facilities.
        </div>

        <div class="search">

            <input
                id="query"
                placeholder="e.g. Where is the computer lab?"
                onkeydown="handleEnter(event)"
            >

            <button class="mic" id="micButton" onclick="startVoice()">
                🎤
            </button>

            <button class="ask" onclick="askAI()">
                Ask
            </button>

        </div>

        <div class="examples">

            <div class="examples-title">
                Try asking
            </div>

            <div class="example"
                 onclick="useExample('Where is the computer lab?')">
                Where is the computer lab?
            </div>

            <div class="example"
                 onclick="useExample('Where is the library?')">
                Where is the library?
            </div>

            <div class="example"
                 onclick="useExample('Where is the principal office?')">
                Where is the principal office?
            </div>

            <div class="example"
                 onclick="useExample('Where is the cafeteria?')">
                Where is the cafeteria?
            </div>

            <div class="example"
                 onclick="useExample('Where is the CS department?')">
                Where is the CS department?
            </div>

        </div>

        <div class="response">

            <div class="response-title">
                AI Response
            </div>

            <div id="responseText" class="response-text">
                Ask me where something is on campus.
            </div>

            <div id="locationCard" class="location-card">

                <div id="locationName" class="location-name"></div>

                <div id="locationInfo" class="location-info"></div>

            </div>

        </div>

    </aside>


    <main class="map-container">

        <div class="map-header">

            <div class="map-title">
                Campus Map
            </div>

            <div class="map-subtitle">
                Interactive campus navigation
            </div>

        </div>


        <svg
            id="map"
            viewBox="0 0 900 650"
            preserveAspectRatio="xMidYMid meet"
        >

            <!-- ROADS -->

            <line
                class="road"
                x1="50"
                y1="350"
                x2="850"
                y2="350"
            />

            <line
                class="road"
                x1="500"
                y1="80"
                x2="500"
                y2="600"
            />

            <line
                class="road-line"
                x1="50"
                y1="350"
                x2="850"
                y2="350"
            />

            <line
                class="road-line"
                x1="500"
                y1="80"
                x2="500"
                y2="600"
            />


            <!-- BUILDINGS -->

            <rect
                class="building"
                x="45"
                y="110"
                width="160"
                height="120"
                rx="10"
            />

            <rect
                class="building"
                x="250"
                y="110"
                width="150"
                height="150"
                rx="10"
            />

            <rect
                class="building"
                x="570"
                y="100"
                width="180"
                height="150"
                rx="10"
            />

            <rect
                class="building"
                x="350"
                y="390"
                width="180"
                height="120"
                rx="10"
            />

            <rect
                class="building"
                x="600"
                y="400"
                width="180"
                height="130"
                rx="10"
            />

            <rect
                class="building"
                x="140"
                y="470"
                width="160"
                height="100"
                rx="10"
            />


            <!-- BUILDING LABELS -->

            <text
                x="125"
                y="170"
                text-anchor="middle"
                class="location-label"
            >
                PARKING
            </text>

            <text
                x="325"
                y="185"
                text-anchor="middle"
                class="location-label"
            >
                ADMIN BLOCK
            </text>

            <text
                x="660"
                y="175"
                text-anchor="middle"
                class="location-label"
            >
                CS BLOCK
            </text>

            <text
                x="440"
                y="455"
                text-anchor="middle"
                class="location-label"
            >
                ACADEMIC BLOCK
            </text>

            <text
                x="690"
                y="465"
                text-anchor="middle"
                class="location-label"
            >
                STUDENT CENTER
            </text>

            <text
                x="220"
                y="520"
                text-anchor="middle"
                class="location-label"
            >
                SCIENCE BLOCK
            </text>


            <!-- ROUTE -->

            <polyline
                id="route"
                class="route"
                points=""
            />


            <!-- LOCATION DOTS -->

            <g id="locations"></g>

        </svg>


        <div class="legend">

            <div class="legend-item">
                <span class="dot-blue"></span>
                Campus location
            </div>

            <div class="legend-item">
                <span class="dot-green"></span>
                Selected destination
            </div>

        </div>

    </main>

</div>


<script>

const locations = {{ locations | safe }};

const svg = document.getElementById("locations");

function createLocations() {

    Object.entries(locations).forEach(([key, location]) => {

        const circle =
            document.createElementNS(
                "http://www.w3.org/2000/svg",
                "circle"
            );

        circle.setAttribute("cx", location.x);
        circle.setAttribute("cy", location.y);
        circle.setAttribute("r", 8);
        circle.classList.add("location-dot");

        circle.dataset.key = key;

        circle.onclick = () => {

            document.getElementById("query").value =
                "Where is " + location.name + "?";

            askAI();
        };

        svg.appendChild(circle);


        const text =
            document.createElementNS(
                "http://www.w3.org/2000/svg",
                "text"
            );

        text.setAttribute("x", location.x + 12);
        text.setAttribute("y", location.y + 5);
        text.classList.add("location-label");
        text.textContent = location.name;

        svg.appendChild(text);

    });

}

createLocations();


function handleEnter(event) {

    if(event.key === "Enter") {
        askAI();
    }

}


function useExample(text) {

    document.getElementById("query").value = text;

    askAI();

}


async function askAI() {

    const input =
        document.getElementById("query");

    const query =
        input.value.trim();

    if(!query) return;


    document.getElementById("responseText").innerText =
        "Thinking...";


    const response =
        await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                query: query
            })

        });


    const data = await response.json();


    if(!data.success) {

        document.getElementById("responseText").innerText =
            data.message;

        document.getElementById("locationCard").style.display =
            "none";

        return;
    }


    document.getElementById("responseText").innerText =
        data.message;


    document.getElementById("locationCard").style.display =
        "block";


    document.getElementById("locationName").innerText =
        data.data.name;


    document.getElementById("locationInfo").innerText =
        data.data.building +
        " • " +
        data.data.floor +
        "\n\n" +
        data.data.description;


    highlightLocation(data.location);


    drawRoute(data.location);


    speak(data.message);

}


function highlightLocation(key) {

    document
        .querySelectorAll(".location-dot")
        .forEach(dot => {

            dot.classList.remove("active");

            if(dot.dataset.key === key) {

                dot.classList.add("active");

            }

        });

}


function drawRoute(key) {

    const location = locations[key];

    if(!location) return;

    const route =
        document.getElementById("route");

    const startX = 500;
    const startY = 350;

    route.setAttribute(
        "points",
        `${startX},${startY} ${location.x},${location.y}`
    );

    route.style.display = "block";

}


function speak(text) {

    if(!("speechSynthesis" in window))
        return;

    window.speechSynthesis.cancel();

    const speech =
        new SpeechSynthesisUtterance(text);

    speech.rate = 0.95;
    speech.pitch = 1;

    window.speechSynthesis.speak(speech);

}


function startVoice() {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if(!SpeechRecognition) {

        alert(
            "Speech recognition is not supported by this browser. Try Chrome."
        );

        return;
    }


    const recognition =
        new SpeechRecognition();

    recognition.lang = "en-US";

    recognition.interimResults = false;

    recognition.continuous = false;


    const button =
        document.getElementById("micButton");


    button.classList.add("active");

    button.innerText = "🔴";


    recognition.start();


    recognition.onresult = function(event) {

        const text =
            event.results[0][0].transcript;

        document.getElementById("query").value =
            text;

        askAI();

    };


    recognition.onerror = function() {

        button.classList.remove("active");

        button.innerText = "🎤";

    };


    recognition.onend = function() {

        button.classList.remove("active");

        button.innerText = "🎤";

    };

}

</script>

</body>
</html>
"""


@app.route("/")
def index():

    import json

    return render_template_string(
        HTML,
        locations=json.dumps(LOCATIONS)
    )


@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    query = data.get("query", "")

    result = process_query(query)

    return jsonify(result)


if __name__ == "__main__":

    print()
    print("=" * 60)
    print("        AI CAMPUS NAVIGATOR")
    print("=" * 60)
    print()
    print("Open:")
    print("http://127.0.0.1:5000")
    print()
    print("Press CTRL+C to stop.")
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )