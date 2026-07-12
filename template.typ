#import "@preview/cetz:0.5.2"

#let size = 40cm
#set page(width: size, height: size, margin: 5mm, background: context layout(l => {
  let gradient = gradient.linear(blue.lighten(90%), white, angle: 90deg)
  rect(width: size, height: size, stroke: none, fill: gradient, {
    image("lpl.svg", width: 90%)
    place(bottom + right, image("pttp.svg", width: 7cm))
  })
}))

#let mainboard = json(bytes(sys.inputs.at("mainboard")))
#let sideboard = json(bytes(sys.inputs.at("sideboard")))
#let score = sys.inputs.at("score", default: "0-0-0")
#let deckname = sys.inputs.at("name", default: "My Deck")
#let date = sys.inputs.at("date", default: "01/01/2026")

#let card-width = 4.5cm
#let grid-inset = 2mm
#let grid-columns = 6
#let stack-spread = 15mm
#let stack-card-width = 5cm
#let badge-style = (
  fill: gray.darken(50%),
  stroke: gray,
  radius: 3mm
)

#set text(font: "Noto Sans")

#let render-card(count, image-filename, width: card-width) = {
  cetz.canvas({
    import cetz.draw: *

    content((0, 0), box(radius: (width / 4cm) * 2mm,
      image(image-filename, width: width), clip: true),
        name: "card")

    circle((rel: (-1mm, -1mm), to: "card.north-east"), ..badge-style, name: "badge")
    content("badge.center", text(12pt, white)[ #count ])
  })
}

#let render-sideboard-divider() = block(inset: grid-inset, {
  cetz.canvas({
    import cetz.draw: *

    set-style(stroke: gray, fill: gray, mark: (length: 1mm, fill: gray))
    scale(y: -1)
    line((0, 0), (0, 2cm), name: "line")
    content("line.end", angle: 90deg, text(gray)[Sideboard], anchor: "east", name: "label", padding: 2mm)
    line("label.west", (0, 20), stroke: gradient.linear(gray, gray.transparentize(100%), angle: 90deg))
  })
})

#align(center, {
  set text(top-edge: "bounds", bottom-edge: "descender")

  grid(columns: 1, inset: 1mm,
    text(20pt)[Lega Pauper Lipsia],
    underline(text(42pt)[#score #deckname]),
    text(14pt)[#date -- 5 Rounds Swiss],
  )
  v(2cm)
})

#let mainboard-grid = grid(columns: grid-columns, inset: grid-inset,
  ..mainboard.map(card => render-card(card.at("count"), card.at("image")))
)

#let sideboard-stack = block(inset: grid-inset, {
  for ((i, card)) in sideboard.enumerate() {
    if i > 0 {
      place(top + left,
        move(dy: i * stack-spread, render-card(card.at("count"), card.at("image"), width: stack-card-width)))
    } else {
      render-card(card.at("count"), card.at("image"), width: stack-card-width)
    }
  }
})


#align(center, grid(columns: 3,
  mainboard-grid, render-sideboard-divider(), sideboard-stack
))