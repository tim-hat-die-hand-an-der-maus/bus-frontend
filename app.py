import dataclasses
from datetime import datetime
from typing import List, Optional

import requests
from dataclasses_json import LetterCase, dataclass_json
from flask import Flask, render_template, send_from_directory

app = Flask("bus", template_folder="flask_templates")
STOPS_CONVERSION_TABLE = {"1": "Abzweig nach Eiche", "2": "Abzweig nach Nedlitz", "3": "Abzw. Betriebshof ViP", "4": "Ketziner Str./Königsweg", "5": "Domstr.", "6": "Am Alten Mörtelwerk", "9": "Alter Markt/Landtag", "10": "Alter Tornow", "11": "Töplitz, Leester Str.", "1 3": "Alt-Kladow", "14": "Alt Nowawes", "15": "Töplitz, Kirschweg", "16": "Wublitzstr./Am Bahnhof", "17": "Am Fenn", "18": "Am Findling/Willi-Frohwein-Platz", "20": "Töplitz, Dorfplatz", "21": "Töplitz, Feuerwehr", "22": "Am Gehölz", "23": "Töplit z, Sportplatz", "27": "Am Hämphorn", "28": "Am Havelblick", "29": "Am Hirtengraben", "34": "Am Küssel", "36": "Am Moosfenn", "39": "Am Neuen Garten/Gr. Weinm.str.", "41": "Am Omnibushof", "42": "Am Pfingstberg", "47": "Am Schragen", "51": "Amunds enstr./Nedlitzer Str.", "52": "Amundsenstr./Potsdamer Str.", "54": "An der Brauerei", "58": "Anhaltstr.", "60": "Campus Jungfernsee", "61": "Auf dem Kiewitt", "62": "Außenweg", "75": "Bassinplatz", "76": "Bhf Park Sanssouci", "77": "Bhf Charlotte nhof", "78": "Bhf Medienstadt Babelsberg", "79": "Bhf Charlottenhof/Geschw.-Scholl-Str.", "80": "Bhf Pirschheide", "81": "Bhf Rehbrücke", "89": "Naturkundemuseum", "90": "Bergholz-Rehbrücke, Verdistr.", "96": "Betriebshof ViP", "100": "Birkenstr. /Alleestr.", "101": "Bisamkiez", "102": "Brunsbütteler Damm/Ruhl. Str.", "103": "Brandenburger Str.", "104": "Brentanoweg", "106": "Volkspark", "107": "Ludwig-Richter-Str.", "108": "Burgstr./Klinikum", "109": "Clara-Schumann-Str./Trebbiner Str.",  "110": "Campus Fachhochschule", "111": "Chopinstr.", "121": "Studio Babelsberg", "125": "Dortustr.", "131": "Drachenhaus", "134": "Drewitzer Str./Am Buchhorst", "135": "Drewitzer Str./E.-Weinert-Str.", "137": "Drewitz-Ort", "140": "E.-Claud.-Str ./Drewitzer Str.", "141": "E.-Claud.-Str./H.-Mann-Allee", "143": "Eichenweg", "144": "Ecksteinweg", "145": "Eichenring", "148": "An der Windmühle", "149": "Kaiserplatz", "150": "Kienhorststr.", "151": "Schloss Sacrow", "152": "Eisbergstücke", "15 3": "Krampnitzsee", "154": "Rotkehlchenweg", "155": "Fahrländer See", "156": "Falkenhorst", "157": "Feuerbachstr.", "158": "Am Upstall", "159": "Schule Fahrland", "160": "Filmpark", "161": "Stadtwerke", "162": "Finkenweg/Brauhausberg", "163": "Fi nkenweg/Leipziger Str.", "165": "Finnenhaus-Siedlung", "168": "Florastr.", "171": "Fontanestr.", "177": "Freiligrathstr.", "179": "Friedenskirche", "180": "Friedhöfe", "183": "Friedrich-Wolf-Str.", "188": "Waldsiedlung Groß Glienicke", "189": "La ndesumweltamt", "190": "Am Park", "191": "Gaußstr.", "192": "Am Urnenfeld", "193": "Kuhforter Damm", "194": "Geiselberg", "195": "Ehrenpfortenbergstr.", "196": "Gerlachstr.", "197": "Baumschulenweg", "198": "Hechtsprung", "199": "Glienicker Brück e", "201": "Birkenweg", "202": "Glumestr.", "203": "Am Schlahn", "204": "Bullenwinkel", "205": "Gößweinsteiner Gang", "206": "Goetheplatz", "207": "Sacrower Allee/Richard-Wagner-Str.", "208": "Friedrich-Günther-Park", "209": "Kirche Golm", "211":  "Science Park West", "212": "Science Park/Universität", "213": "Zum Großen Herzberg", "214": "Alt-Golm", "215": "Golmer Fichten", "217": "Am Anger", "218": "Kirche Groß Glienicke", "219": "Hannes-Meyer-Str.", "222": "Hans-Albers-Str.", "226": "H ebbelstr.", "227": "Heerstr./Wilhelmstr.", "228": "Luisenplatz-Nord/Park Sanssouci", "231": "Heinrich-von-Kleist-Str.", "236": "Hermann-Maaß-Str.", "240": "Höhenstr.", "241": "Holzmarktstr.", "242": "Horstweg/Großbeerenstr.", "247": "Hubertusdamm /Steinstr.", "248": "Hugstraße", "249": "Kirche Bornim", "250": "Humboldtring/L.-Pulewka-Str.", "251": "Humboldtring/Nuthestr.", "260": "Im Bogen/Forststr.", "261": "Im Bogen/Zeppelinstr.", "263": "In der Aue", "265": "Institut für Agrartechnik",  "271": "Jägertor/Justizzentrum", "273": "Jagdhausstr.", "274": "Johan-Bouman-Platz", "275": "Johannes-Kepler-Platz", "279": "Am Grünen Weg", "281": "Kaiser-Friedrich-Str./Polizei", "282": "Karolinenhöhe", "284": "Karl-Marx-Str./Behringstr.", "28 5": "Hiroshima-Nagasaki-Platz", "286": "Kirche Kartzow", "287": "Kaserne Hottengrund", "288": "Im Winkel", "289": "Kastanienallee/Zeppelinstr.", "290": "Kirschallee", "291": "Kläranlage Potsdam-Nord", "292": "Katjes", "293": "Kleine Str.", "296":  "Konrad-Wolf-Allee/Sternstr.", "298": "Kreuzstr.", "300": "Küsselstr.", "302": "Kunersdorfer Str.", "306": "Zum Telegrafenberg", "307": "Lange Brücke", "308": "Landschaftsfriedhof Gatow", "309": "Schiffbauergasse/Uferweg", "310": "Kleine Weinmei sterstr.", "311": "Langhansstr./Große Weinm.str.", "313": "Weinmeisterstr.", "314": "Klinikum", "315": "Lerchensteig/Kleingartenanlage", "316": "Lilienthalstr.", "317": "Camp. Universität/Lindenallee", "318": "Lindstedter Chaussee", "319": "Leest , Eichholzweg", "320": "Leest, Kirche", "323": "Luftschiffhafen", "324": "Luisenplatz-Süd/Park Sanssouci", "325": "Luisenplatz-Ost/Park Sanssouci", "331": "Magnus-Zeller-Platz", "332": "Schule Marquardt", "333": "Mangerstr.", "334": "Marie-Juchac z-Str.", "335": "Mauerstr.", "337": "Max-Born-Str.", "338": "Mehlbeerenweg", "339": "Eisenbahnbrücke Marquardt", "340": "Schloss Marquardt", "341": "Am Wald", "342": "Fährweg", "343": "Melanchthonplatz", "344": "Metzer Str.", "345": "Hoffbauer-St iftung", "351": "Nauener Tor", "356": "Neuend. Str./Mend.-Barth.-Str.", "358": "Neues Palais", "360": "Bassewitz", "361": "Heinrich-Heine-Weg", "362": "Römerschanze", "363": "Plantagenweg", "364": "Neukladower Allee", "368": "Töplitz, Zur alten F ähre", "369": "Neu Töplitz, Weinbergstr.", "371": "Orangerie/Botanischer Garten", "372": "Neu Töplitz, Wendeplatz", "375": "Otto-Erich-Str.", "376": "Otto-Hahn-Ring", "380": "Paaren", "381": "Parnemannweg", "387": "Plantagenstr.", "389": "Platz d er Einheit/Bildungsforum", "390": "Platz der Einheit/Nord", "392": "Platz der Einheit/West", "393": "Platz der Einheit/Ost", "394": "Persiusstr.", "395": "Puschkinallee", "396": "Priesterweg", "399": "Rathaus Babelsberg", "400": "Rathaus", "403":  "Rote-Kreuz-Str.", "404": "S+U Rathaus Spandau", "405": "Ritterfelddamm/Potsdamer Ch.", "409": "Reiterweg/Alleestr.", "410": "Reiterweg/Jägerallee", "413": "Rodensteinstr.", "414": "Robert-Baberske-Str.", "416": "Rückertstr.", "418": "Ruinenberg str.", "420": "Satzkorn", "421": "Sacrower See", "422": "S Hauptbahnhof/Nord ILB", "423": "S Hauptbahnhof", "424": "S Hauptbahnhof/Friedrich-Engels-Str.", "426": "S Babelsberg/Lutherplatz", "427": "S Babelsberg/Schulstr.", "428": "S Babelsberg/Wa ttstr.", "432": "S Griebnitzsee Bhf/Süd", "433": "Scheffelstr.", "435": "Karl-Liebknecht-Stadion", "437": "Schilfhof", "438": "Schillerplatz/Schafgraben", "439": "Schlaatzstr.", "440": "Schiffbauergasse/Berliner Str.", "441": "Schlegelstr./Pappel allee", "442": "Schloss Babelsberg", "443": "Schloss Cecilienhof", "444": "Schloss Charlottenhof", "446": "Schloss Sanssouci/Bornstedter Str.", "447": "Schloss Sanssouci", "448": "Schloßstr.", "449": "Schlänitzseer Weg", "450": "Schlüterstr./Fors tstr.", "451": "Kienheide", "452": "Schneiderremise", "454": "Seeburg, Gemeindeamt", "457": "Schwimmhalle am Brauhausberg", "459": "Sonnenlandstr.", "461": "Spindelstr.", "463": "Sportplatz Bornim", "464": "Sporthalle", "465": "Seeburg, Havelland halle", "466": "Stahnsdorfer Brücke", "467": "Stahnsd. Str./A.-Bebel-Str.", "468": "Seeburg, Engelsfelde", "470": "Steinstücken", "472": "Sternwarte", "473": "Stern-Center/Gerlachstr.", "474": "Stern-Center/Nuthestr.", "479": "Telegrafenberg", "4 81": "Temmeweg", "484": "Templiner Eck", "487": "Thaerstr.", "488": "Gutsstr.", "491": "Hermann-Struve-Str.", "492": "Studentenwohnheim Eiche", "494": "Tornowstr.", "497": "Trebbiner Str.", "499": "TÜV-Akademie", "501": "Turmstr.", "506": "Zum He izwerk", "508": "Kirche Uetz", "511": "Übergang", "515": "Unter den Eichen", "517": "Viereckremise", "518": "Rote Kaserne", "523": "Waldstr./Horstweg", "530": "Weinmeisterweg", "532": "Weißer See", "534": "Werderscher Damm/Forststr.", "536": "Wie senstr./Lotte-Pulewka-Str.", "538": "Weinmeisterhornweg", "541": "Zedlitzberg", "543": "Zum Bhf Pirschheide", "544": "Ziegelhof", "545": "Zum Kahleberg", "546": "Theodor-Fontane-Str.", "600": "Auf dem Kiewitt", "601": "Hermannswerder", "602": "Ca mpus Jungfernsee/Nedlitzer Str.", "701": "S Wannsee", "705": "Expressbus", "710": "Rosa-Luxemburg-Schule", "711": "Grundschule am Humboldtring", "712": "Grundschule Hanna von Pestalozza", "713": "Karl-Foerster-Schule", "714": "Gundschule Max Dort u", "715": "Zeppelin-Grundschule", "716": "Montessori-Oberschule", "717": "Grundschule Bruno H. Bürgel", "718": "Schule am Griebnitzsee", "719": "Theodor-Fontane-Oberschule", "720": "Förderschule 42/44", "721": "Weidenhof-Grundschule", "724": "Sc hwimmhalle am Brauhausberg", "725": "Kiezbad Am Stern", "811": "Bhf Golm", "812": "Sacrow-Paretzer Kanal", "813": "Am Heineberg", "814": "Rotdornweg/Stahnsdorfer Str.", "815": "Lindenpark", "816": "Bhf Rehbrücke/Süd", "848": "Am Schragen/Russisch e Kolonie", "849": "Rote Kaserne/Nedlitzer Str.", "900": "Betriebshof", "901": "Betriebshof Babelsberg Bus", "902": "Fähre", "903": "Abstellung Platz der Einheit", "920": "Betriebshof Subunternehmer", "970": "S Nikolassee", "971": "Wannseebadweg" , "972": "Badeweg", "973": "Wasserwerk Beelitzhof", "974": "Am Sandwerder", "975": "Tillmannsweg", "976": "Wannseebrücke", "977": "Am Kleinen Wannsee", "978": "Wernerstr.", "979": "Pfaueninselchaussee/Königstr.", "980": "Rathaus Wannsee", "981":  "Schuchardtweg", "982": "Friedenstr.", "983": "Schäferberg", "984": "Nikolskoer Weg", "985": "Schloss Glienicke", "986": "Glienicker Lake", "994": "Katharinenholzstraße", "997": "Virtueller Betriebshof.", "998": "Betriebshof SEV"}

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
