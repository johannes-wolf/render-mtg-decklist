#import "@preview/cetz:0.5.2"

#let mainboard = if "mainboard" in sys.inputs {
  json(bytes(sys.inputs.at("mainboard")))
} else {
  json("mainboard.json")
}
#let sideboard = if "sideboard" in sys.inputs {
  json(bytes(sys.inputs.at("sideboard")))
} else {
  json("sideboard.json")
}
#let score = sys.inputs.at("score", default: "0-0-0")
#let deckname = sys.inputs.at("name", default: "My Deck")
#let date = sys.inputs.at("date", default: "01/01/2026")

#let stack-x-spread = 12mm
#let stack-y-spread = 34mm
#let card-width = 180mm
#let grid-inset = 1mm
#let grid-columns = 5
#let sideboard-gap = 42mm

// Text height
#let lega-size = 24mm
#let name-size = 56mm
#let date-size = 18mm

#set text(font: "Noto Sans")

// We render with 25.4 PPI so that 1 mm = 1 px
#let size = 1280mm
#set page(width: size, height: size, margin: 20mm, background: context layout(l => {
  let gradient = gradient.linear(blue.lighten(90%), white, angle: 90deg)
  rect(width: size, height: size, stroke: none, fill: gradient, {
    image("lpl.svg", width: 90%)
    place(bottom + right, move(dx: -1cm, dy: -1cm, image("pttp.svg", width: 19cm)))
  })
}))

#let render-card-stack(cards, alternate-x: false) = {
  let width = card-width
  let count = cards.len()

  // We re-crop the images with a runded corner to get rid
  // of some image artifacts scryfalls card images have.
  let card-image(card) = box(radius: (width / 4cm) * 2mm,
    image(card, width: width), clip: true)

  cetz.canvas({
    import cetz.draw: *

    for ((i, card)) in cards.enumerate() {
      let x-offset = if alternate-x { calc.rem(i, 2) } else { 0 } * stack-x-spread

      content((x-offset, (count - i) * stack-y-spread), card-image(card), name: "card")
    }
  })
}

// Show the title
#align(center, {
  set text(top-edge: "bounds", bottom-edge: "descender")

  grid(columns: 1, inset: 2mm,
    text(lega-size)[Lega Pauper Lipsia],
    underline(text(name-size)[#score #deckname]),
    text(date-size)[#date -- 5 Rounds Swiss],
  )
})

#let flatten-cards(cards) = {
  let flat = ()
  for item in cards {
    for i in range(0, item.at("count", default: 1)) {
      flat.push(item.at("image"))
    }
  }
  return flat
}

#let mainboard-grid = grid(columns: grid-columns, inset: grid-inset,
  ..flatten-cards(mainboard).chunks(4).map(card => render-card-stack(card))
)

#let sideboard-stack = block(inset: grid-inset,
  render-card-stack(flatten-cards(sideboard), alternate-x: true)
)

#align(center, block(inset: (bottom: 0mm, rest: 20mm), grid(columns: 3,
  mainboard-grid, h(sideboard-gap), sideboard-stack
)))
