---
title: Indice Documentazione ContextBundler
copyright: © 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
author: IK0VCK
type: index
product: Turbo-AI Tools
solution: ContextBundler
project: ContextBundler
version: 1.1
updated: 2026-08-11
---
# Indice Documentazione

## context-request-<descrizione>.md

Elenco puntuale di path relativi alla solution, uno per riga, che ContextBundler
deve includere nel bundle. Nessun wildcard, nessuna istruzione in linguaggio
naturale: solo path esatti (verificati con list-files se non certi).

Per estrarre solo alcune righe di un file invece del file intero, aggiungere
uno o più range dopo il path. Esempio con doppio range sullo stesso file:

    MyProject/Services/Exporter.cs:120-180,340-410
