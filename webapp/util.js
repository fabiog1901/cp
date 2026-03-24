const funnyWords = [
  "abracadabra",
  "amazeballs",
  "arglebargle",
  "awesomesauce",
  "balderdash",
  "bamboozle",
  "bazinga",
  "brouhaha",
  "bubblegum",
  "buckaroo",
  "bumfuzzle",
  "cacophony",
  "catawampus",
  "chortle",
  "codswallop",
  "collywobbles",
  "defenestrate",
  "dillydally",
  "dingbat",
  "doohickey",
  "flabbergasted",
  "flapdoodle",
  "flibbertigibbet",
  "flummox",
  "folderol",
  "gadzooks",
  "gobbledygook",
  "goofball",
  "hocuspocus",
  "hodgepodge",
  "hootenanny",
  "hornswoggle",
  "hullabaloo",
  "humdinger",
  "jabberwocky",
  "jamboree",
  "kerfuffle",
  "knickknack",
  "kookaburra",
  "lollygag",
  "malarkey",
  "mumbojumbo",
  "nincompoop",
  "poppycock",
  "rigmarole",
  "skedaddle",
  "thingamabob",
  "whatchamacallit",
  "whimsy",
  "widdershins",
  "wonky",
  "yippee",
  "zoinks",
];

function getFunnyName() {
  const pick = () => funnyWords[Math.floor(Math.random() * funnyWords.length)];
  return `${pick()}-${pick()}`;
}

function getHumanSize(valueInGb) {
  const suffixes = ["kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "RB", "QB"];
  const base = 1000;
  const bytes = Number(valueInGb) * 1_000_000_000;

  if (!Number.isFinite(bytes) || bytes <= 0) {
    return `0 ${suffixes[0]}`;
  }

  const exponent = Math.min(
    Math.floor(Math.log(bytes) / Math.log(base)),
    suffixes.length - 1,
  );
  const scaled = bytes / base ** exponent;
  const rounded = scaled.toFixed(1);

  if (rounded.endsWith(".0")) {
    return `${rounded.slice(0, -2)} ${suffixes[exponent]}`;
  }
  return `${rounded} ${suffixes[exponent]}`;
}

window.CPUtil = {
  getFunnyName,
  getHumanSize,
};
