// Add a background color, some padding, and rounded corners to code blocks
#show raw.where(block: true): it => block(
  fill: rgb("#f4f4f5"),
  inset: 8pt,
  radius: 4pt,
  width: 100%,
  it
)

// Add extra space underneath all headings
#show heading: set block(above: 2em, below: 1em)

// Add a faint blue background and left border to blockquotes
#show quote.where(block: true): it => block(
  above: 1em, // <-- This pulls the quote closer to the text above it
  below: 1em,   // Keep a nice standard gap below the quote
  fill: rgb("#eff5fa"), 
  inset: 12pt,
  radius: 4pt,
  stroke: (left: 4pt + rgb("#a1c2e3")), 
  width: 100%,
  it
)

// Make links a gentle, modern blue
#show link: set text(fill: rgb("#3b82f6"))

// Tighten the gap above all bulleted lists
#show list: set block(above: 1em, below: 1em)