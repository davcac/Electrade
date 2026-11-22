#!/usr/bin/env python
"""Aggiorna i grafici PNG del master e rigenera sempre AGGIORNATA.pptx.

Il master puo contenere immagini complete chiamate GRAFICO_n oppure i vecchi
segnaposto {{GRAFICO_n}}. Testi, note, impaginazione e grafici nativi restano
quelli del master.
"""

import os
from pathlib import Path, PurePosixPath
import posixpath
import re
from tempfile import NamedTemporaryFile
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "Presentazione_Electrade_MASTER.pptx"
UPDATED = ROOT / "Presentazione_Electrade_AGGIORNATA.pptx"

CHARTS = {
    "GRAFICO_1": "slide_1_prezzi_pun_zone/grafici/01_serie_prezzi_mgp_DAILY.png",
    "GRAFICO_2": "slide_1_prezzi_pun_zone/grafici/01_serie_prezzi_mgp.png",
    "GRAFICO_3": "slide_1_prezzi_pun_zone/grafici/04_serie_per_zona.png",
    "GRAFICO_4": "slide_2_scelta_evento_p_zero/grafici/01_serie_per_zona_novembre.png",
    "GRAFICO_5": "slide_2_scelta_evento_p_zero/grafici/02_serie_per_zona_12_13_novembre.png",
    "GRAFICO_6": "slide_4_carico_production/grafici/01_produzione_carico_7zone.png",
    "GRAFICO_7": "slide_4_carico_production/grafici/02_surplus_7zone.png",
    "GRAFICO_8": "slide_4_carico_production/grafici/02_surplus_3zone.png",
    "GRAFICO_9": "slide_5_mappa_transiti/nuovo/grafici/import_export_linee_48h.png",
    "GRAFICO_10": "slide_5_mappa_transiti/nuovo/grafici/04_surplus_adj_3zone.png",
    "GRAFICO_11": "slide_5_mappa_transiti/nuovo/grafici/macrozone_48h.png",
    "GRAFICO_12": "slide_5_mappa_transiti/nuovo/grafici/export_sud_centrosud.png",
    "GRAFICO_14": "slide_4_carico_production/grafici/05_surplus_macrozone.png",
    "GRAFICO_15": "slide_5_mappa_transiti/nuovo/grafici/05_surplus_adj_macrozone.png",
}

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
RELS = "http://schemas.openxmlformats.org/package/2006/relationships"
TYPES = "http://schemas.openxmlformats.org/package/2006/content-types"
MARKER = re.compile(r"\{\{(GRAFICO_\w+)\}\}")
IMAGE_MARKER = re.compile(r"GRAFICO_\w+")


def relationships_part(part):
    part = PurePosixPath(part)
    return str(part.parent / "_rels" / (part.name + ".rels"))


def resolve_target(part, target):
    return target.lstrip("/") if target.startswith("/") else posixpath.normpath(
        posixpath.join(posixpath.dirname(part), target)
    )


def slide_parts(package):
    presentation = "ppt/presentation.xml"
    deck = minidom.parseString(package.read(presentation))
    relations = minidom.parseString(package.read(relationships_part(presentation)))
    targets = {
        link.getAttribute("Id"): link.getAttribute("Target")
        for link in relations.getElementsByTagNameNS(RELS, "Relationship")
    }
    for slide in deck.getElementsByTagNameNS(P, "sldId"):
        target = targets[slide.getAttributeNS(R, "id")]
        yield target.lstrip("/") if target.startswith("/") else posixpath.normpath(f"ppt/{target}")


def picture(shape, marker, rel_id, filename):
    document = shape.ownerDocument
    properties = shape.getElementsByTagNameNS(P, "cNvPr")[0]
    transforms = shape.getElementsByTagNameNS(A, "xfrm")
    if len(transforms) != 1:
        raise ValueError(f"Posizione del segnaposto {marker} non definita nel master.")

    template = minidom.parseString(f"""
        <p:pic xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}">
          <p:nvPicPr><p:cNvPr/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>
          <p:blipFill><a:blip/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
          <p:spPr><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
        </p:pic>
    """)
    image = document.importNode(template.documentElement, deep=True)
    image_properties = image.getElementsByTagNameNS(P, "cNvPr")[0]
    image_properties.setAttribute("id", properties.getAttribute("id"))
    image_properties.setAttribute("name", marker)
    image_properties.setAttribute("descr", filename)
    image.getElementsByTagNameNS(A, "blip")[0].setAttributeNS(R, "r:embed", rel_id)
    geometry = image.getElementsByTagNameNS(A, "prstGeom")[0]
    geometry.parentNode.insertBefore(transforms[0].cloneNode(deep=True), geometry)
    return image


def updated_parts(source, assets):
    changes = {}
    inserted = set()
    targets = {}
    for part in slide_parts(source):
        slide = minidom.parseString(source.read(part))
        proxies = []
        pictures = []
        for image in slide.getElementsByTagNameNS(P, "pic"):
            properties = image.getElementsByTagNameNS(P, "cNvPr")
            if len(properties) != 1:
                raise ValueError(f"Proprieta immagine non valide in {part}.")
            marker = properties[0].getAttribute("name")
            if IMAGE_MARKER.fullmatch(marker):
                pictures.append((marker, image))
        for shape in slide.getElementsByTagNameNS(P, "sp"):
            text = "".join(
                node.data
                for run in shape.getElementsByTagNameNS(A, "t")
                for node in run.childNodes
                if node.nodeType == node.TEXT_NODE
            )
            match = MARKER.fullmatch(text.strip())
            if match:
                proxies.append((match[1], shape))
        if not proxies and not pictures:
            continue

        rel_part = relationships_part(part)
        relations = minidom.parseString(source.read(rel_part))
        rel_ids = {
            link.getAttribute("Id")
            for link in relations.getElementsByTagNameNS(RELS, "Relationship")
        }
        links = {
            link.getAttribute("Id"): link
            for link in relations.getElementsByTagNameNS(RELS, "Relationship")
        }
        for marker, image in pictures:
            if marker not in assets or marker in inserted:
                raise ValueError(f"Grafico sconosciuto o duplicato nel master: {marker}.")
            blips = image.getElementsByTagNameNS(A, "blip")
            if len(blips) != 1:
                raise ValueError(f"Immagine del grafico {marker} non valida.")
            rel_id = blips[0].getAttributeNS(R, "embed")
            link = links.get(rel_id)
            if link is None or link.getAttribute("Type") != f"{R}/image":
                raise ValueError(f"Collegamento immagine mancante per {marker}.")
            if link.getAttribute("TargetMode") == "External":
                raise ValueError(f"Il grafico {marker} deve essere incorporato nel master.")
            target = resolve_target(part, link.getAttribute("Target"))
            if not target.lower().endswith(".png") or target not in source.namelist():
                raise ValueError(f"Componente PNG del grafico {marker} non valido: {target}.")
            if target in changes and changes[target] != assets[marker]:
                raise ValueError(f"Immagine condivisa da grafici diversi: {target}.")
            changes[target] = assets[marker]
            targets[marker] = target
            inserted.add(marker)
        rel_number = 1
        for marker, shape in proxies:
            if marker not in assets or marker in inserted:
                raise ValueError(f"Segnaposto sconosciuto o duplicato nel master: {marker}.")
            while f"rId{rel_number}" in rel_ids:
                rel_number += 1
            rel_id = f"rId{rel_number}"
            rel_ids.add(rel_id)
            target = f"ppt/media/electrade-{marker.lower()}.png"

            link = relations.createElementNS(RELS, "Relationship")
            link.setAttribute("Id", rel_id)
            link.setAttribute("Type", f"{R}/image")
            link.setAttribute("Target", posixpath.relpath(target, posixpath.dirname(part)))
            relations.documentElement.appendChild(link)

            image = picture(shape, marker, rel_id, Path(CHARTS[marker]).stem)
            shape.parentNode.replaceChild(image, shape)
            changes[target] = assets[marker]
            targets[marker] = target
            inserted.add(marker)

        if proxies:
            changes[part] = slide.toxml(encoding="utf-8")
            changes[rel_part] = relations.toxml(encoding="utf-8")

    missing = assets.keys() - inserted
    if missing:
        raise ValueError(f"Segnaposto mancanti nel master: {', '.join(sorted(missing))}.")

    content_types = minidom.parseString(source.read("[Content_Types].xml"))
    defaults = content_types.getElementsByTagNameNS(TYPES, "Default")
    if not any(item.getAttribute("Extension").lower() == "png" for item in defaults):
        png = content_types.createElementNS(TYPES, "Default")
        png.setAttribute("Extension", "png")
        png.setAttribute("ContentType", "image/png")
        overrides = content_types.getElementsByTagNameNS(TYPES, "Override")
        content_types.documentElement.insertBefore(png, overrides[0] if overrides else None)
        changes["[Content_Types].xml"] = content_types.toxml(encoding="utf-8")
    return changes, targets


def build_presentation(master, output):
    master, output = Path(master), Path(output)
    if master.resolve() == output.resolve():
        raise ValueError("Master e versione aggiornata devono essere file diversi.")
    assets = {}
    for marker, name in CHARTS.items():
        data = (ROOT / name).read_bytes()
        if not (data.startswith(b"\x89PNG\r\n\x1a\n") and data.endswith(b"IEND\xaeB\x60\x82")):
            raise ValueError(f"PNG non valido o incompleto: {name}.")
        assets[marker] = data

    with NamedTemporaryFile(dir=output.parent, prefix=".electrade-", suffix=".tmp", delete=False) as tmp:
        temporary = Path(tmp.name)
    try:
        with ZipFile(master) as source, ZipFile(temporary, "w") as generated:
            changes, targets = updated_parts(source, assets)
            for part in source.infolist():
                data = changes.pop(part.filename) if part.filename in changes else source.read(part)
                generated.writestr(part, data)
            for name, data in changes.items():
                generated.writestr(ZipInfo(name), data, compress_type=ZIP_DEFLATED)

        with ZipFile(temporary) as generated:
            invalid = generated.testzip()
            if invalid:
                raise ValueError(f"Componente del PowerPoint illeggibile: {invalid}.")
            for marker, data in assets.items():
                if generated.read(targets[marker]) != data:
                    raise ValueError(f"Verifica del grafico {marker} fallita.")

        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    try:
        build_presentation(MASTER, UPDATED)
    except PermissionError as error:
        raise SystemExit(f"File bloccato. Chiudi la presentazione in PowerPoint e riprova. ({error})") from error
    except (OSError, ValueError, BadZipFile, ExpatError, KeyError) as error:
        raise SystemExit(f"Rigenerazione interrotta. L'ultima versione resta disponibile. ({error})") from error
    with ZipFile(UPDATED) as generated:
        count = len(list(slide_parts(generated)))
    print(f"Aggiornato {UPDATED.name}: {count} slide, {len(CHARTS)} grafici PNG aggiornati.")


if __name__ == "__main__":
    main()
