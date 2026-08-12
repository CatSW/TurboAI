---
title: Changelog ContextBundler
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
type: changelog
product: Turbo-AI Tools
solution: ContextBundler
project: ContextBundler
version: 1.0
license: MIT
updated: 2026-08-12
---
# Changelog ContextBundler

Redatto seguendo le convenzioni di [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/)

## [Unreleased] - 2026-08-12

### Added

- T2.3: test per l’opzione `--base64` (flag false/true, validità base64, round-trip decode). Rimosso warning xUnit2020 (`Assert.Fail`).
- T2.2: conversione reale dell’output in base64 quando è presente `--base64` (UTF-8 → `Convert.ToBase64String` standard senza line-break). Compatibile con `--stdout`.
- T2.1: gestione opzione CLI `--base64` (parsing, passaggio fino a `BundleResult.ToBase64`). Conversione reale dell’output in base64 demandata a T2.2.

### Changed

- T1.2 Rimosso l'escaping di `<`/`>` in `[LT]`/`[GT]` introdotto in v1.1 (T1.2): il contenuto dei file torna a essere inserito nel bundle senza alterazioni. Aggiornato di conseguenza il test golden sul CDATA XML e rimossa la nota ormai obsoleta in `00-Indice-Documentazione.md`.
- T1.1 Ripristinati i delimitatori di fence dei blocchi file nel bundle da `[[[FILE ...]]]`/`[[[END FILE]]]` a `<<<FILE ...>>>`/`<<<END FILE>>>` (T1.1). L'escaping di `<`/`>` nel contenuto (`[LT]`/`[GT]`) resta invariato per ora, verrà ripristinato in T1.2.

## [1.1.0] - 2026-08-11

### Changed

- escaping dei caratteri < e > in [LT] e [GT] nei file XML
- fence dei file con [[[ e ]]] per evitare che il parser di alcuni chat tools li interpreti come tag XML

## [1.0.0] - 2026-08-09

### Added
- primo rilascio pubblico del tool

---  

[@IK0VCK]: https://github.com/IK0VCK
