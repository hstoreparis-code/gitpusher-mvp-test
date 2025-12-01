ULTRA-HD PLACEHOLDER SETUP

Les fichiers UHD (1x/2x/3x, WebP/AVIF/PNG) doivent être ajoutés ultérieurement par la CI/CD dans:
- /public/cdn/hero/
- /public/cdn/logo/
- /public/cdn/banners/
- /public/cdn/components/

Pour chaque image logique (ex: hero, logo, banner):
- Créer les variantes suivantes:
  - [NAME]@1x.png, [NAME]@2x.png, [NAME]@3x.png
  - [NAME]@1x.webp, [NAME]@2x.webp, [NAME]@3x.webp
  - [NAME]@1x.avif, [NAME]@2x.avif, [NAME]@3x.avif

Les pages HTML utilisent déjà des balises <picture> pointant vers ces chemins.
