import dataclasses
import datetime
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
    actual_relative_time: int
    actual_time: str
    direction: str
    mixedTime: str
    passageid: str
    pattern_text: str
    planned_time: str
    route_id: str
    status: str
    trip_id: str
    vehicle_id: str
    vias: Optional[List[str]] = None
    time_class: str = "punctual"

    def set_time_class(self):
        planned = datetime.datetime.strptime(self.planned_time, "%H:%M")
        actual = datetime.datetime.strptime(self.actual_time, "%H:%M")

        diff = planned - actual
        if diff.days < 0:
            if abs(diff.seconds) > 300:
                self.time_class = "delayed"
            else:
                self.time_class = "late"
        else:
            if diff.seconds != 0:
                self.time_class = "early"


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
    [info.set_time_class() for info in content.actual]

    kwargs = {
        "stop": content
    }
    return render_template("index.html", **kwargs)
