# pnpink-assets

Public asset repository for [PnPInk](https://github.com/xoellijo/pnpink).

- Website / gallery: https://xoellijo.github.io/pnpink-assets/
- PnPInk repository: https://github.com/xoellijo/pnpink
- PnPInk guide: https://xoellijo.github.io/pnpink/
- PnPInk forum: https://boardgamegeek.com/guild/4569

## What This Repository Is For

`pnpink-assets` is a companion repository for `PnPInk`.

Its purpose is to host reusable visual assets that can be referenced directly from PnPInk projects instead of being manually downloaded, copied, and organized for every deck or board.

The idea is simple:

- keep assets public and easy to browse
- make them usable from PnPInk with short source paths
- support practical tabletop workflows such as cards, counters, overlays, icons, frames, backgrounds, and decorative pieces
- let authors compose many components from datasets such as CSV or Google Sheets with minimal manual asset handling

## How It Is Intended To Be Used

The main use case is direct consumption from `PnPInk`.

In a template-driven project, a dataset cell should be able to reference an asset from this repository and let PnPInk fetch it, scale it, rotate it, and place it automatically inside a placeholder or across many generated components.

Typical examples include:

- inserting icons or decorative parts into cards
- reusing counters, badges, borders, and panels across multiple products
- composing decks from many small visual pieces instead of from pre-flattened final images
- keeping datasets lightweight while the asset library remains centralized and reusable

This repository is not meant to document internal implementation details of PnPInk sources.
It is meant to remain stable as a public asset library, even if the internal loading logic evolves.

## License

Unless explicitly stated otherwise for a specific file or folder, assets in this repository are published under **CC0 1.0 Universal**.

That means they are intended to be as reusable as possible inside PnPInk projects and beyond.

## Notes

- This repository may contain both hand-made and AI-assisted assets.
- The website and index are generated automatically on push.
- Asset organization may evolve over time, but the goal remains the same: simple public reuse from PnPInk.
