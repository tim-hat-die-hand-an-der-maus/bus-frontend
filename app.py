import dataclasses
from typing import List, Optional

import requests
from dataclasses_json import LetterCase, dataclass_json
from flask import Flask, render_template, send_from_directory

app = Flask("bus", template_folder="flask_templates")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory('public', "favicon.ico")


@app.route("/public/<path:path>")
def public(path: str):
    return send_from_directory('public', path)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclasses.dataclass
class StopInfo:
    actualRelativeTime: int
    actualTime: str
    direction: str
    mixedTime: str
    passageid: str
    patternText: str
    plannedTime: str
    routeId: str
    status: str
    tripId: str
    vehicleId: str
    vias: Optional[List[str]] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclasses.dataclass
class Stop:
    actual: List[StopInfo]


def get_stop(stop_number: int = 180):
    req = requests.get(
        f"https://www.swp-potsdam.de/internetservice/services/passageInfo/stopPassages/stop?stop={stop_number}&mode=departure&language=en")

    if req.ok:
        js = req.json()
        return Stop.from_dict(js)

    return None


@app.route('/', defaults={'stop_number': 180})
@app.route('/<stop_number>')
def index(stop_number: int):
    content: Stop = get_stop(stop_number)

    kwargs = {
        "stop": content
    }
    return render_template("index.html", **kwargs)
