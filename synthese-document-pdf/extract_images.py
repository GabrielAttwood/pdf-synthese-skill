#!/usr/bin/env python3
"""Extrait les images contenues dans un PDF.

Pourquoi : un agent IA lit souvent un PDF en le convertissant en texte. Mais
beaucoup de documents (scans, mises en page graphiques, tableaux et figures
intégrés en image) ont une partie de leur contenu *uniquement* dans des images.
Ce script parcourt les pages, inspecte les objets image (/XObject de sous-type
/Image), décode leurs données et les écrit sur disque (PNG/JPG selon la source),
pour que l'agent puisse ensuite les *regarder*.

Usage :
    python3 extract_images.py <document.pdf> [dossier_sortie]

Le dossier de sortie vaut "images/" par défaut. Les fichiers sont nommés
page<NNN>_<NNN>_<nom>.<ext> pour conserver l'ordre de lecture.

Dépendances : pypdf (et Pillow pour le décodage de certains formats).
    pip install pypdf pillow
"""

import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    sys.exit("pypdf manquant. Installer avec : pip install pypdf pillow")


def extract_images(pdf_path: str, out_dir: str = "images") -> int:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(pdf_path)
    count = 0

    for page_num, page in enumerate(reader.pages, start=1):
        # page.images parcourt les /XObject de type image, décode les données
        # (get_data + filtres /DCTDecode, /FlateDecode, /JPXDecode...) et expose
        # à la fois les octets bruts (.data) et un objet image Pillow (.image).
        for image in page.images:
            count += 1
            stem = f"page{page_num:03d}_{count:03d}"

            # On normalise tout en PNG : certains PDF stockent les figures et
            # tableaux en JPEG 2000 (.jp2), un format que beaucoup d'agents et de
            # viewers ne savent pas lire. Passer par Pillow garantit un PNG lisible.
            pil = getattr(image, "image", None)
            if pil is not None:
                if pil.mode in ("CMYK", "P", "LA", "RGBA"):
                    pil = pil.convert("RGB")
                pil.save(out / f"{stem}.png")
            else:
                # Repli : pas de Pillow → on écrit les octets bruts tels quels.
                with open(out / f"{stem}_{image.name}", "wb") as f:
                    f.write(image.data)

    if count == 0:
        print(f"Aucune image trouvée dans {pdf_path} "
              f"(le document est probablement purement textuel).")
    else:
        print(f"{count} image(s) extraite(s) dans « {out}/ ».")
    return count


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage : python3 extract_images.py <document.pdf> [dossier_sortie]")
    pdf = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "images"
    extract_images(pdf, out)
