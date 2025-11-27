Deploy to Render — instructions

1) Crée une nouvelle service sur Render (Web Service) et connecte-le à ce dépôt GitHub. Tu peux utiliser Dockerfile présent dans le repo ou laisser Render builder automatiquement.

2) Récupère l'`Service ID` depuis la page de ton service Render (Settings → Service ID) et ton `API Key` depuis Render (Account → API Keys).

3) Dans GitHub, va dans `Settings > Secrets and variables > Actions` du dépôt et ajoute deux secrets:
   - `RENDER_API_KEY` : la clé API Render
   - `RENDER_SERVICE_ID` : l'ID du service Render

4) Pousse sur la branche `main`. Le workflow `.github/workflows/deploy-render.yml` déclenchera une requête vers l'API Render pour lancer un déploiement.

Notes:
- Si tu préfères que Render construise automatiquement à chaque push (recommandé), tu peux aussi configurer le déploiement GitHub depuis l'interface Render et ne pas utiliser ce workflow.
- Si tu veux que j'automatise encore plus (ex: création automatique du service via l'API), donne-moi l'autorisation API et je peux préparer un script de provisioning, mais attention aux permissions.
