# pnpink-assets

**pnpink-assets** is a companion repository for **PnPInk**.

It is meant to host reusable image collections that can later be consumed as a dedicated PnPInk source.
For now, it is intentionally simple: folders and filenames.

## Purpose

This repository is designed to:

- keep reusable asset packs outside the main `pnpink` code repository
- version image collections independently from the extension code
- provide a stable folder structure for future source resolvers
- make it easy to browse, copy, and reuse assets directly by path

## Current Philosophy

At this stage, the repository stays deliberately lightweight.

There is no catalog, manifest, or database layer.
The structure is based only on:

- folders
- subfolders
- filenames

That keeps the repository easy to maintain and easy to inspect by humans.

## Structure

A typical structure looks like this:

```txt
pnpink-assets/
  CC0/
    birds/
      birds.png
      worm1.png
      worm2.png
      egg1.png
      ...
  IA/
    badges/
      gold_circle1.png
      wood_rect1.png
      ...
    banners/
    corners/
    decorations/
    edges/
    icons/
    panels/
```

## Naming

The repository currently relies on filenames as the asset identifiers.

That means the practical reference model is simply:

- category folder
- subfolder
- filename

Examples:

```txt
CC0/birds/worm1.png
IA/icons/crown1.png
IA/panels/parchment3.png
```

For now, this is enough.
Later, PnPInk can add a source resolver on top of this structure without forcing a different repository layout.

## Intended Future Integration

The goal is to support a future PnPInk source that reads assets directly from this repository.

The exact syntax can be decided later, but the repository is being organized with that future use in mind.

Possible examples could look like:

```txt
@{pnp://IA/icons/crown1.png}
@{pnp://CC0/birds/worm1.png}
```

The important part for now is keeping the folder structure stable and the filenames clean.

## Recommendations

To keep the repository usable over time:

- prefer short, stable, descriptive filenames
- avoid spaces when possible
- keep related assets grouped in clear folders
- treat folder paths as part of the public structure
- only reorganize folders when there is a clear benefit

## Relationship with PnPInk

This repository is not part of the main PnPInk codebase.

It is a separate asset repository intended to complement PnPInk projects and, later, to integrate with a dedicated source resolver.

