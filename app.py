import dataclasses
from datetime import datetime
from typing import List, Optional

import requests
from dataclasses_json import LetterCase, dataclass_json
from flask import Flask, render_template, send_from_directory

app = Flask("bus", template_folder="flask_templates")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory('public', "favicon.jpg")


@app.route("/public/<path:path>")
def public(path: str):
    return send_from_directory('public', path)


TIME_UNIT_CONVERSION_TABLE = {
    "%UNIT_MIN%": "min"
}


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclasses.dataclass
class Alert:
    pass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclasses.dataclass
class Route:
    alerts: List[Alert]
    authority: str
    directions: List[str]
    id: str
    name: str
    route_type: str
    short_name: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclasses.dataclass
class StopInfo:
    actual_relative_time: int
    direction: str
    mixed_time: str
    passageid: str
    pattern_text: str
    planned_time: str
    route_id: str
    status: str
    trip_id: str
    vias: Optional[List[str]] = None
    time_class: str = "punctual"
    mixed_time_unit: str = ""
    actual_time: str = ""
    vehicle_id: str = ""
    vehicle_type: str = ""
    route: Optional[Route] = None

    def update(self, routes: List[Route] = None):
        self.update_mixed_time()
        self.set_time_class()
        self.update_vias()

        route = [route for route in routes if route.short_name == self.pattern_text]
        if route:
            self.route = route[0]
            self.set_route_information()

    def update_vias(self):
        if self.vias:
            self.vias = [via.replace("via ", "") for via in self.vias]

    def set_route_information(self):
        self.vehicle_type = self.route.route_type.capitalize()

    def update_mixed_time(self):
        s = self.mixed_time.split(" ")
        if len(s) < 2:
            return

        self.mixed_time = s[0]
        self.mixed_time_unit = TIME_UNIT_CONVERSION_TABLE[s[1]]

    def set_time_class(self):
        if self.actual_time is None or self.mixed_time_unit == "":
            return

        planned = datetime.strptime(self.planned_time, "%H:%M")
        actual = datetime.strptime(self.actual_time, "%H:%M")

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
    stopName: str
    routes: List[Route]


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

    [info.update(content.routes) for info in content.actual]

    kwargs = {
        "stop": content,
        "time": datetime.now().strftime("%H:%M")
    }

    # PyCharm doesn't recognize the changed templates folder
    # noinspection PyUnresolvedReferences
    return render_template("index.html", **kwargs)
