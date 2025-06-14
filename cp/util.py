import random
import math

funny_words = [
    "abominable",
    "abracadabra",
    "abso-bloody-lutely",
    "absquatulate",
    "aflac",
    "aglet",
    "alacazam",
    "amazeballs",
    "amusing",
    "antimacassar",
    "aplomb",
    "appaloosa",
    "arfvedsonite",
    "argle-bargle",
    "avoirdupois",
    "awesomesauce",
    "balderdash",
    "ballyhoo",
    "bamboozle",
    "bazinga",
    "bibble",
    "blatherskite",
    "bling",
    "bloviate",
    "blubber",
    "blubber-buttocks",
    "blubber-nugget",
    "blubberbutt",
    "blunderbuss",
    "bonanza",
    "boob",
    "boondoggle",
    "bootylicious",
    "brouhaha",
    "brouillard",
    "bubblegum",
    "buckaroo",
    "bumfuzzle",
    "bumpkin",
    "bunkum",
    "cacafuego",
    "cacophony",
    "cacophony",
    "callipygian",
    "caper",
    "catawampus",
    "catty-corner",
    "cattywampus",
    "cheeseball",
    "cheesecake",
    "chockablock",
    "chortle",
    "chuck",
    "chucklesome",
    "cockalorum",
    "codswallop",
    "cogito",
    "collywobbles",
    "comical",
    "crapulence",
    "criminy",
    "cuckoo",
    "cumberbund",
    "defenestrate",
    "defenestration",
    "dilly-dally",
    "dilly-whacker",
    "dillydally",
    "ding",
    "dingbat",
    "dingleberry",
    "diphthong",
    "dipsomaniac",
    "dirty",
    "doo-dad",
    "doo-hickey",
    "doodlebug",
    "doofer",
    "doohickey",
    "doozy",
    "dork",
    "dorkwad",
    "droll",
    "druthers",
    "dunderhead",
    "eargasm",
    "earlobe",
    "earwiggle",
    "eccentric",
    "eccentricity",
    "eclectic",
    "egghead",
    "eggplant",
    "egregious",
    "elixir",
    "enigma",
    "entertaining",
    "ersatz",
    "erstwhile",
    "eskimo",
    "eureka",
    "exquisite",
    "extravaganza",
    "eyesore",
    "fandango",
    "fart",
    "fartlek",
    "fiddle-faddle",
    "fiddlesticks",
    "flabbergasted",
    "flaparoo",
    "flapdoodle",
    "flapjack",
    "flibbertigibbet",
    "flimflam",
    "flotsam",
    "fluffball",
    "fluffernutter",
    "flummox",
    "flummoxed",
    "folderol",
    "folly",
    "fracas",
    "frisson",
    "froth",
    "fuddy-duddy",
    "furryboo",
    "fuzz",
    "gadzooks",
    "giddy",
    "glabella",
    "glitchy",
    "gobbledygook",
    "gobbledygrump",
    "gobbledygum",
    "gobsmacked",
    "goober",
    "goofball",
    "goofy",
    "gorgonzola",
    "grouchy",
    "grumpkin",
    "gubbins",
    "guffa",
    "guffaw",
    "guffaw",
    "gunk",
    "haberdashery",
    "harum-scarum",
    "higgledy-piggledoo",
    "higgledy-piggledy",
    "hilar",
    "hilarious",
    "hinky",
    "hobnob",
    "hocus-pocus",
    "hocus-pocus",
    "hodgepodge",
    "hoodwink",
    "hooey",
    "hoopla",
    "hooptie",
    "hoot",
    "hootenanny",
    "hornswoggle",
    "hullabaloo",
    "humdinger",
    "humorous",
    "hunkydory",
    "ibbly",
    "ickle",
    "icky",
    "idjit",
    "iffy",
    "iggly",
    "iggur",
    "immy",
    "inglo",
    "ingy",
    "inky",
    "ipsy",
    "itchy",
    "ixora",
    "izzle",
    "jabber",
    "jabberwocky",
    "jamboree",
    "jangle",
    "jankety",
    "janky",
    "jazzy",
    "jeroboam",
    "jibber-jabber",
    "jiggery-pokery",
    "jiggly",
    "jinx",
    "jinxed",
    "jitterbug",
    "jocular",
    "jocund",
    "jolly",
    "jovial",
    "juked",
    "kablooie",
    "kaboodle",
    "kajigger",
    "kaput",
    "kazaam",
    "kerfuffle",
    "kibble",
    "kibosh",
    "kittenish",
    "klutz",
    "knick-knack",
    "kookaburra",
    "kookiness",
    "kooky",
    "kudzu",
    "lackadaisical",
    "laughable",
    "lick",
    "lickety-lick",
    "lickety-split",
    "lickspittle",
    "lighthearted",
    "lilliputian",
    "logorrhea",
    "lolly",
    "lollygag",
    "lollygagger",
    "lollypop",
    "looney",
    "looniness",
    "loopy",
    "lopsided",
    "lugubrious",
    "lummox",
    "lurky",
    "malarkey",
    "malarky",
    "megalomania",
    "megalomaniac",
    "meme",
    "mirthful",
    "mischief",
    "monkeyshines",
    "mooch",
    "moonstruck",
    "muddle",
    "muddle-puddle",
    "muddleheaded",
    "muffin-top",
    "mumbo-jumbo",
    "munchkin",
    "mushy",
    "nannygoat",
    "natter",
    "natty",
    "nefarious",
    "nerd",
    "nerdvana",
    "nettlesome",
    "nibbly",
    "nincompoop",
    "ninnyhammer",
    "nonsense",
    "noodle",
    "noodle",
    "noodle-doodle",
    "noodle-poodle",
    "noodlehead",
    "nubbly",
    "nurtural",
    "nutso",
    "obnoxious",
    "oddball",
    "oglethorpe",
    "okey-dokey",
    "okey-dokey",
    "olio",
    "onomatopoeia",
    "oodles",
    "oogle",
    "oomph",
    "oopsie-daisy",
    "oopsy",
    "orangutan",
    "ornery",
    "outlandish",
    "oxymoron",
    "palooza",
    "pandemonium",
    "pickle",
    "piddle",
    "piddle-paddle",
    "piffle",
    "piffle",
    "pizzazz",
    "playful",
    "plop",
    "pooch",
    "poodle-doodle",
    "poofy",
    "poop",
    "popcorn",
    "poppycock",
    "popsicle",
    "prattle",
    "pudding",
    "puff",
    "puke",
    "pumpernickel",
    "quackery",
    "quackish",
    "quaggy",
    "quagmire",
    "quailish",
    "quenchless",
    "quibble",
    "quilted",
    "quipster",
    "quirky",
    "ragamuffin",
    "rambunctious",
    "ramshackle",
    "rapscallion",
    "razz",
    "razzadorable",
    "razzberry",
    "razzle-dazzle",
    "razzmatazz",
    "rib-tickling",
    "rigmarole",
    "rinky",
    "rinky-dink",
    "roister",
    "rubberneck",
    "rumpus",
    "sassafras",
    "scallywag",
    "schnozzle",
    "scrumptious",
    "scuttlebutt",
    "shenanigans",
    "silly",
    "skedaddle",
    "skedoodle",
    "skibbereen",
    "skimp",
    "skullduggery",
    "snark",
    "snazzy",
    "snicker-snack",
    "snickerdoodle",
    "snickersnee",
    "snollygolly",
    "snollygoster",
    "snort",
    "spiff",
    "spiffy",
    "squooshy",
    "taradiddle",
    "tater tot",
    "tchotchke",
    "thingamabob",
    "thingamajig",
    "tickle",
    "tiddlywinks",
    "tinkle",
    "tiptoe",
    "tizzy",
    "tomfoolery",
    "toodle",
    "toodle-oo",
    "toolshed",
    "toot",
    "tootle",
    "twaddle",
    "twang",
    "twerp",
    "twiddle",
    "uber",
    "udder",
    "ululate",
    "umpteen",
    "unctuous",
    "undertaker",
    "unicorn",
    "unicycle",
    "uppity",
    "uproarious",
    "va-va-voom",
    "vagabond",
    "vamoose",
    "vandalism",
    "veggie",
    "vex",
    "viscous",
    "vixen",
    "voodoo",
    "vuvuzela",
    "wackadoo",
    "wacky",
    "waggish",
    "wazoo",
    "whatchamacallit",
    "whims",
    "whimsical",
    "whimsy",
    "whippersnapper",
    "whirligig",
    "wibble",
    "wiggleworm",
    "wimp",
    "witty",
    "wobbly",
    "wonky",
    "wuss",
    "xerox",
    "xylophone",
    "yahoo",
    "yellow-belly",
    "yippee",
    "yodel",
    "yoink",
    "yuck",
    "yucks",
    "zany",
    "ziggurat",
    "zilch",
    "zing",
    "zoinks",
    "zonked",
    "zoom",
    "zounds",
    "zygote",
]


def get_funny_name():
    return "-".join(random.choices(funny_words, k=2))


def get_human_size(
    value_in_gb: float
) -> str:
    """
    1500 --> 1.5 TB
    500  --> 500 GB
    2000 --> 2 TB
    """
    suffix = (
        " kB",
        " MB",
        " GB",
        " TB",
        " PB",
        " EB",
        " ZB",
        " YB",
        " RB",
        " QB",
    )

    base = 1000
    bytes_ = float(value_in_gb * 1_000_000_000)

    exp = int(min(math.log(abs(bytes_), base), len(suffix)))
    human_size = "%.1f" % (bytes_ / (base**exp)) 

    if human_size[-2:] == ".0":
        return human_size[:-2] + suffix[exp - 1]
    return human_size + suffix[exp - 1]


