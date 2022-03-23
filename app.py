import dataclasses
from datetime import datetime
from typing import List, Optional

import requests
from dataclasses_json import LetterCase, dataclass_json
from flask import Flask, render_template, send_from_directory

app = Flask("bus", template_folder="flask_templates")
STOPS_CONVERSION_TABLE = {"903": "Abstellung Platz der Einheit", "3": "Abzw. Betriebshof ViP", "1": "Abzweig nach Eiche", "2": "Abzweig nach Nedlitz", "14": "Alt Nowawes", "214": "Alt-Golm", "13": "Alt-Kladow", "9": "Alter Markt/Landtag", "10": "Alter Tornow", "6": "Am Alten M\u00f6rtelwerk", "217": "Am Anger", "17": "Am Fenn", "18": "Am Findling/Willi-Frohwein-Platz", "22": "Am Geh\u00f6lz", "279": "Am Gr\u00fcnen Weg", "28": "Am Havelblick", "813": "Am Heineberg", "29": "Am Hirtengraben", "27": "Am H\u00e4mphorn", "977": "Am Kleinen Wannsee", "34": "Am K\u00fcssel", "36": "Am Moosfenn", "39": "Am Neuen Garten/Gr. Weinm.str.", "41": "Am Omnibushof", "190": "Am Park", "42": "Am Pfingstberg", "974": "Am Sandwerder", "203": "Am Schlahn", "47": "Am Schragen", "848": "Am Schragen/Russisch e Kolonie", "158": "Am Upstall", "192": "Am Urnenfeld", "341": "Am Wald", "51": "Amunds enstr./Nedlitzer Str.", "52": "Amundsenstr./Potsdamer Str.", "54": "An der Brauerei", "148": "An der Windm\u00fchle", "58": "Anhaltstr.", "61": "Auf dem Kiewitt", "600": "Auf dem Kiewitt", "62": "Au\u00dfenweg", "972": "Badeweg", "360": "Bassewitz", "75": "Bassinplatz", "197": "Baumschulenweg", "90": "Bergholz-Rehbr\u00fccke, Verdistr.", "900": "Betriebshof", "901": "Betriebshof Babelsberg Bus", "998": "Betriebshof SEV", "920": "Betriebshof Subunternehmer", "96": "Betriebshof ViP", "77": "Bhf Charlotte nhof", "79": "Bhf Charlottenhof/Geschw.-Scholl-Str.", "811": "Bhf Golm", "78": "Bhf Medienstadt Babelsberg", "76": "Bhf Park Sanssouci", "80": "Bhf Pirschheide", "81": "Bhf Rehbr\u00fccke", "816": "Bhf Rehbr\u00fccke/S\u00fcd", "100": "Birkenstr. /Alleestr.", "201": "Birkenweg", "101": "Bisamkiez", "103": "Brandenburger Str.", "104": "Brentanoweg", "102": "Brunsb\u00fctteler Damm/Ruhl. Str.", "204": "Bullenwinkel", "108": "Burgstr./Klinikum", "602": "Ca mpus Jungfernsee/Nedlitzer Str.", "317": "Camp. Universit\u00e4t/Lindenallee", "110": "Campus Fachhochschule", "60": "Campus Jungfernsee", "111": "Chopinstr.", "109": "Clara-Schumann-Str./Trebbiner Str.", "5": "Domstr.", "125": "Dortustr.", "131": "Drachenhaus", "137": "Drewitz-Ort", "134": "Drewitzer Str./Am Buchhorst", "135": "Drewitzer Str./E.-Weinert-Str.", "140": "E.-Claud.-Str ./Drewitzer Str.", "141": "E.-Claud.-Str./H.-Mann-Allee", "144": "Ecksteinweg", "195": "Ehrenpfortenbergstr.", "145": "Eichenring", "143": "Eichenweg", "152": "Eisbergst\u00fccke", "339": "Eisenbahnbr\u00fccke Marquardt", "705": "Expressbus", "155": "Fahrl\u00e4nder See", "156": "Falkenhorst", "157": "Feuerbachstr.", "163": "Fi nkenweg/Leipziger Str.", "160": "Filmpark", "162": "Finkenweg/Brauhausberg", "165": "Finnenhaus-Siedlung", "168": "Florastr.", "171": "Fontanestr.", "177": "Freiligrathstr.", "179": "Friedenskirche", "982": "Friedenstr.", "180": "Friedh\u00f6fe", "208": "Friedrich-G\u00fcnther-Park", "183": "Friedrich-Wolf-Str.", "902": "F\u00e4hre", "342": "F\u00e4hrweg", "720": "F\u00f6rderschule 42/44", "191": "Gau\u00dfstr.", "194": "Geiselberg", "196": "Gerlachstr.", "199": "Glienicker Br\u00fcck e", "986": "Glienicker Lake", "202": "Glumestr.", "206": "Goetheplatz", "215": "Golmer Fichten", "717": "Grundschule Bruno H. B\u00fcrgel", "712": "Grundschule Hanna von Pestalozza", "711": "Grundschule am Humboldtring", "714": "Gundschule Max Dort u", "488": "Gutsstr.", "205": "G\u00f6\u00dfweinsteiner Gang", "226": "H ebbelstr.", "219": "Hannes-Meyer-Str.", "222": "Hans-Albers-Str.", "198": "Hechtsprung", "227": "Heerstr./Wilhelmstr.", "361": "Heinrich-Heine-Weg", "231": "Heinrich-von-Kleist-Str.", "236": "Hermann-Maa\u00df-Str.", "491": "Hermann-Struve-Str.", "601": "Hermannswerder", "28 5": "Hiroshima-Nagasaki-Platz", "345": "Hoffbauer-St iftung", "241": "Holzmarktstr.", "242": "Horstweg/Gro\u00dfbeerenstr.", "247": "Hubertusdamm /Steinstr.", "248": "Hugstra\u00dfe", "250": "Humboldtring/L.-Pulewka-Str.", "251": "Humboldtring/Nuthestr.", "240": "H\u00f6henstr.", "260": "Im Bogen/Forststr.", "261": "Im Bogen/Zeppelinstr.", "288": "Im Winkel", "263": "In der Aue", "265": "Institut f\u00fcr Agrartechnik", "273": "Jagdhausstr.", "274": "Johan-Bouman-Platz", "275": "Johannes-Kepler-Platz", "271": "J\u00e4gertor/Justizzentrum", "281": "Kaiser-Friedrich-Str./Polizei", "149": "Kaiserplatz", "713": "Karl-Foerster-Schule", "435": "Karl-Liebknecht-Stadion", "284": "Karl-Marx-Str./Behringstr.", "282": "Karolinenh\u00f6he", "287": "Kaserne Hottengrund", "289": "Kastanienallee/Zeppelinstr.", "994": "Katharinenholzstra\u00dfe", "292": "Katjes", "4": "Ketziner Str./K\u00f6nigsweg", "451": "Kienheide", "150": "Kienhorststr.", "725": "Kiezbad Am Stern", "249": "Kirche Bornim", "209": "Kirche Golm", "218": "Kirche Gro\u00df Glienicke", "286": "Kirche Kartzow", "508": "Kirche Uetz", "290": "Kirschallee", "293": "Kleine Str.", "310": "Kleine Weinmei sterstr.", "314": "Klinikum", "291": "Kl\u00e4ranlage Potsdam-Nord", "296": "Konrad-Wolf-Allee/Sternstr.", "15 3": "Krampnitzsee", "298": "Kreuzstr.", "193": "Kuhforter Damm", "302": "Kunersdorfer Str.", "300": "K\u00fcsselstr.", "189": "La ndesumweltamt", "308": "Landschaftsfriedhof Gatow", "307": "Lange Br\u00fccke", "311": "Langhansstr./Gro\u00dfe Weinm.str.", "319": "Leest , Eichholzweg", "320": "Leest, Kirche", "315": "Lerchensteig/Kleingartenanlage", "316": "Lilienthalstr.", "815": "Lindenpark", "318": "Lindstedter Chaussee", "107": "Ludwig-Richter-Str.", "323": "Luftschiffhafen", "228": "Luisenplatz-Nord/Park Sanssouci", "325": "Luisenplatz-Ost/Park Sanssouci", "324": "Luisenplatz-S\u00fcd/Park Sanssouci", "331": "Magnus-Zeller-Platz", "333": "Mangerstr.", "334": "Marie-Juchac z-Str.", "335": "Mauerstr.", "337": "Max-Born-Str.", "338": "Mehlbeerenweg", "343": "Melanchthonplatz", "344": "Metzer Str.", "716": "Montessori-Oberschule", "89": "Naturkundemuseum", "351": "Nauener Tor", "369": "Neu T\u00f6plitz, Weinbergstr.", "372": "Neu T\u00f6plitz, Wendeplatz", "356": "Neuend. Str./Mend.-Barth.-Str.", "358": "Neues Palais", "364": "Neukladower Allee", "984": "Nikolskoer Weg", "371": "Orangerie/Botanischer Garten", "375": "Otto-Erich-Str.", "376": "Otto-Hahn-Ring", "380": "Paaren", "381": "Parnemannweg", "394": "Persiusstr.", "979": "Pfaueninselchaussee/K\u00f6nigstr.", "387": "Plantagenstr.", "363": "Plantagenweg", "389": "Platz d er Einheit/Bildungsforum", "390": "Platz der Einheit/Nord", "393": "Platz der Einheit/Ost", "392": "Platz der Einheit/West", "396": "Priesterweg", "395": "Puschkinallee", "400": "Rathaus", "399": "Rathaus Babelsberg", "980": "Rathaus Wannsee", "409": "Reiterweg/Alleestr.", "410": "Reiterweg/J\u00e4gerallee", "405": "Ritterfelddamm/Potsdamer Ch.", "414": "Robert-Baberske-Str.", "413": "Rodensteinstr.", "710": "Rosa-Luxemburg-Schule", "814": "Rotdornweg/Stahnsdorfer Str.", "518": "Rote Kaserne", "849": "Rote Kaserne/Nedlitzer Str.", "403": "Rote-Kreuz-Str.", "154": "Rotkehlchenweg", "418": "Ruinenberg str.", "362": "R\u00f6merschanze", "416": "R\u00fcckertstr.", "426": "S Babelsberg/Lutherplatz", "427": "S Babelsberg/Schulstr.", "428": "S Babelsberg/Wa ttstr.", "432": "S Griebnitzsee Bhf/S\u00fcd", "423": "S Hauptbahnhof", "424": "S Hauptbahnhof/Friedrich-Engels-Str.", "422": "S Hauptbahnhof/Nord ILB", "970": "S Nikolassee", "701": "S Wannsee", "404": "S+U Rathaus Spandau", "812": "Sacrow-Paretzer Kanal", "207": "Sacrower Allee/Richard-Wagner-Str.", "421": "Sacrower See", "420": "Satzkorn", "724": "Sc hwimmhalle am Brauhausberg", "433": "Scheffelstr.", "440": "Schiffbauergasse/Berliner Str.", "309": "Schiffbauergasse/Uferweg", "437": "Schilfhof", "438": "Schillerplatz/Schafgraben", "439": "Schlaatzstr.", "441": "Schlegelstr./Pappel allee", "442": "Schloss Babelsberg", "443": "Schloss Cecilienhof", "444": "Schloss Charlottenhof", "985": "Schloss Glienicke", "340": "Schloss Marquardt", "151": "Schloss Sacrow", "447": "Schloss Sanssouci", "446": "Schloss Sanssouci/Bornstedter Str.", "448": "Schlo\u00dfstr.", "449": "Schl\u00e4nitzseer Weg", "450": "Schl\u00fcterstr./Fors tstr.", "452": "Schneiderremise", "981": "Schuchardtweg", "159": "Schule Fahrland", "332": "Schule Marquardt", "718": "Schule am Griebnitzsee", "457": "Schwimmhalle am Brauhausberg", "983": "Sch\u00e4ferberg", "211": "Science Park West", "212": "Science Park/Universit\u00e4t", "468": "Seeburg, Engelsfelde", "454": "Seeburg, Gemeindeamt", "465": "Seeburg, Havelland halle", "459": "Sonnenlandstr.", "461": "Spindelstr.", "464": "Sporthalle", "463": "Sportplatz Bornim", "161": "Stadtwerke", "467": "Stahnsd. Str./A.-Bebel-Str.", "466": "Stahnsdorfer Br\u00fccke", "470": "Steinst\u00fccken", "473": "Stern-Center/Gerlachstr.", "474": "Stern-Center/Nuthestr.", "472": "Sternwarte", "492": "Studentenwohnheim Eiche", "121": "Studio Babelsberg", "479": "Telegrafenberg", "4 81": "Temmeweg", "484": "Templiner Eck", "487": "Thaerstr.", "719": "Theodor-Fontane-Oberschule", "546": "Theodor-Fontane-Str.", "975": "Tillmannsweg", "494": "Tornowstr.", "497": "Trebbiner Str.", "501": "Turmstr.", "499": "T\u00dcV-Akademie", "23": "T\u00f6plit z, Sportplatz", "20": "T\u00f6plitz, Dorfplatz", "21": "T\u00f6plitz, Feuerwehr", "15": "T\u00f6plitz, Kirschweg", "11": "T\u00f6plitz, Leester Str.", "368": "T\u00f6plitz, Zur alten F \u00e4hre", "515": "Unter den Eichen", "517": "Viereckremise", "997": "Virtueller Betriebshof.", "106": "Volkspark", "188": "Waldsiedlung Gro\u00df Glienicke", "523": "Waldstr./Horstweg", "971": "Wannseebadweg", "976": "Wannseebr\u00fccke", "973": "Wasserwerk Beelitzhof", "721": "Weidenhof-Grundschule", "538": "Weinmeisterhornweg", "313": "Weinmeisterstr.", "530": "Weinmeisterweg", "532": "Wei\u00dfer See", "534": "Werderscher Damm/Forststr.", "978": "Wernerstr.", "536": "Wie senstr./Lotte-Pulewka-Str.", "16": "Wublitzstr./Am Bahnhof", "541": "Zedlitzberg", "715": "Zeppelin-Grundschule", "544": "Ziegelhof", "543": "Zum Bhf Pirschheide", "213": "Zum Gro\u00dfen Herzberg", "506": "Zum He izwerk", "545": "Zum Kahleberg", "306": "Zum Telegrafenberg", "511": "\u00dcbergang"}

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
    stop_name: str
    stop_short_name: str
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

    try:
        [info.update(content.routes) for info in content.actual]
    except AttributeError:
        return "This stop doesn't exist"

    kwargs = {
        "stop": content,
        "time": datetime.now().strftime("%H:%M"),
        "stops_map": STOPS_CONVERSION_TABLE,
    }

    # PyCharm doesn't recognize the changed templates folder
    # noinspection PyUnresolvedReferences
    return render_template("index.html", **kwargs)
