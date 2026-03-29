# Markdown-to-DOCX Round-trip Style Guide

This file contains only math syntax that survives pandoc md-to-docx-to-md round-tripping as a fixed point, followed by warnings about unstable syntax.

## Stable Inline Math

The quadratic formula is $x = \frac{- b \pm \sqrt{b^{2} - 4ac}}{2a}$.

Einstein's famous equation: $E = mc^{2}$.

A summation: $\sum_{i = 1}^{n}i = \frac{n(n + 1)}{2}$.

Greek letters inline: $\alpha,\beta,\gamma,\delta,\epsilon$.

## Stable Display Math

The Gaussian integral:

$$\int_{- \infty}^{\infty}e^{- x^{2}}\, dx = \sqrt{\pi}$$

A matrix:

$$\begin{pmatrix}
a & b \\
c & d
\end{pmatrix}\begin{pmatrix}
x \\
y
\end{pmatrix} = \begin{pmatrix}
ax + by \\
cx + dy
\end{pmatrix}$$

An aligned environment:

$$\begin{aligned}
\nabla \cdot \mathbf{E} & = \frac{\rho}{\epsilon_{0}} \\
\nabla \cdot \mathbf{B} & = 0 \\
\nabla \times \mathbf{E} & = - \frac{\partial\mathbf{B}}{\partial t} \\
\nabla \times \mathbf{B} & = \mu_{0}\mathbf{J} + \mu_{0}\epsilon_{0}\frac{\partial\mathbf{E}}{\partial t}
\end{aligned}$$

## Stable Mixed Content

Here is a paragraph with **bold**, *italic*, and math: $\mathcal{L} = \frac{1}{2}\partial_{\mu}\phi\partial^{\mu}\phi - V(\phi)$.

A numbered list with math:

1.  The derivative of $f(x) = x^{n}$ is $f'(x) = nx^{n - 1}$.

2.  The integral $\int_{0}^{1}x^{2}\, dx = \frac{1}{3}$.

3.  The limit $\lim_{n \rightarrow \infty}\left( 1 + \frac{1}{n} \right)^{n} = e$.

## Stable Blockquote

> This is a blockquote. It renders with a light blue background, a blue left border, and indentation on both sides. Round-trips cleanly through DOCX.

Nested blockquotes are not supported --- pandoc flattens them to a single level in DOCX, losing the nesting. Avoid nested \> \> syntax. TODO: find a way to support nested blockquotes. If you need to display nested block quotes as a code block, you can still do that:


    > Outer blockquote.
    >
    > > Inner nested blockquote.
    >
    > Back to outer.

## Stable Advanced Math

Calligraphic and blackboard bold: $\mathcal{F}$, $\mathbb{R}$, $\mathbf{v}$.

A fraction tower: $\frac{1}{1 + \frac{1}{1 + \frac{1}{x}}}$.

## Stable Delimiters

Parentheses: $\left( \frac{a}{b} \right)$

Braces: $\left\{ \frac{a}{b} \right\}$

Pipes: $\left| \frac{a}{b} \right|$

Floor: $\left\lfloor \frac{a}{b} \right\rfloor$

Ceiling: $\left\lceil \frac{a}{b} \right\rceil$

Brackets: $\left\lbrack \frac{a}{b} \right\rbrack$

## Stable Accents and Decorations

Use $\widehat{x}$, not $\widehat{x}$ (converts to widehat anyway).

Use $\overrightarrow{x}$, not $\overrightarrow{x}$ (converts to overrightarrow anyway).

Use $\widetilde{x}$, not $\widetilde{x}$ (converts to widetilde anyway).

These are stable: $\bar{x}$, $\dot{x}$.

## Stable Spacing

Use $a\, b$ for thin space, not $a\ b$ (converts to backslash-space).

Use $a\quad b$ for quad space.

## Stable Dots

$a,\ldots,z$ and $a + \cdots + z$ and $\vdots$ and $\ddots$.

## Stable Text in Math

$x\text{ for all }x$ and $x\text{if }y$ and $x\text{ if}y$.

## Stable Operators

$\lim_{x \rightarrow 0}\frac{\sin x}{x}$

## Stable Table

  -----------------------------------------------------------------------------------------------
  Symbol   Name             Formula
  -------- ---------------- ---------------------------------------------------------------------
  $\pi$    Pi               $\pi = \frac{C}{d}$

  $e$      Euler's number   $e = \lim_{n \rightarrow \infty}\left( 1 + \frac{1}{n} \right)^{n}$

  $\phi$   Golden ratio     $\phi = \frac{1 + \sqrt{5}}{2}$
  -----------------------------------------------------------------------------------------------

## Table Column Alignment

Use colons in the pipe-table separator to control alignment. This is respected by both DOCX (pandoc) and PDF renderers.


    |:---| = left    |---:| = right    |:---:| = center    |----| = default (left)

Center short/numeric columns; left-align text-heavy columns:

  ----------------------------------------------------------------------------------------------------------------
      Belief      Assertion                                                        Prior           Posterior
  --------------- ------------------------------------------------------------ ------------- ---------------------
        37        Bile acid sequestrants decrease the hepatic bile acid pool       0.96              0.25

        13        Dietary saturated fat increases hepatic cholesterol              0.88              0.20
  ----------------------------------------------------------------------------------------------------------------

## Syntax Warnings (Unstable on Round-trip)

Use $\lbrack x\rbrack$, not $\lbrack x\rbrack$ (converts to lbrack/rbrack anyway).

Use $\widehat{x}$, not $\widehat{x}$ (converts to widehat on first trip, then stable).

Use $\overrightarrow{x}$, not $\overrightarrow{x}$ (converts to overrightarrow on first trip, then stable).

Use $\widetilde{x}$, not $\widetilde{x}$ (converts to widetilde on first trip, then stable).

Use $a\, b$, not $a\ b$ (colon-space converts to backslash-space on first trip, then stable).

Use ${argmax}_{x}f(x)$, not ${argmax}_{x}f(x)$ (loses operatorname wrapper on first trip, then stable).

AVOID invisible delimiters (left-dot and right-dot) entirely. They accumulate a trailing backslash-space on every round-trip and never stabilize. This includes begin-cases, which converts to left-brace begin-matrix ... end-matrix right-dot.

AVOID left-double-pipe/right-double-pipe. They break into left-dot parallel/right-dot parallel and then drift.

AVOID semicolon-space (converts to mspace) and negative-space (removed entirely).
