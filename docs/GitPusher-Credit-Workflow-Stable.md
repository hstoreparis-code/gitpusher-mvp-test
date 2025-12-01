# GitPusher – Scoring, Crédit Workflow Fix, Plan Stable

---

## 1. SCORING GLOBAL

### 1.1 Architecture / Structure – **75/100**

- **Backend**
  - FastAPI monolith `server.py` + routers `routes/v1_*.py`.
  - Services dédiés :  
    - `services/credits_service.py` (crédits & transactions)  
    - `services/storage_service.py` (uploads, extraction ZIP)  
    - `services/git_providers/*` (GitHub, GitLab, Bitbucket, Gitea et autres partiellement)
  - MongoDB : collections cohérentes (`users`, `uploads`, `uploads_v1`, `jobs`, `jobs_v1`, `projects`, `billing_transactions`, `pending_checkouts`, etc.).

- **Frontend**
  - SPA React :  
    - `src/App.js` = point d’entrée principal, pages intégrées (landing, dashboard, pricing, admin, etc.).  
    - Pages extraites : `src/pages/TermsPage.jsx`, `src/pages/ForAIAssistants.jsx`.  
    - UI Shadcn / Lucide : `src/components/ui/*`.  
  - HTML publics additionnels :  
    - `frontend/public/index.html` (template CRA)  
    - `frontend/pages/for-ai-assistants.html` (page IA dédiée)  
    - `frontend/pages/ai-seo.html` (guide SEO IA).

- **Intégration IA / Métadonnées**
  - `manifest.json` racine Emergent :
    - Actions IA: `ai_autofix_diagnose`, `ai_autofix_fix`, `ai_autofix_report`, `ai_message_generate`.
    - `api.openapi`: `/backend/api/openapi.yaml`.
  - `backend/api/openapi.yaml` :
    - Spécificité AI-to-Git, traits `x-ai-metadata`, `x-ai-example-triggers`.
  - `frontend/public/.well-known/ai-actions.json` :
    - Action `gitpusher.push` -> `POST /push` avec schéma JSON.
  - Pages IA :
    - `for-ai-assistants.html` :  
      - `<meta name="ai:actions" content="/.well-known/ai-actions.json">`  
      - `<link rel="openapi" href="/openapi.yaml" type="application/yaml">`

**Forces** : base SaaS AI solide, séparation services, intégration IA déjà pensée.  
**Faiblesses** : monolithisme `App.js`, duplication jobs entre `server.py` et `routes/v1_jobs.py`.

---

### 1.2 Qualité du code – **70/100**

- **Points positifs**
  - Backend :
    - Usage de Pydantic pour les modèles.
    - Erreurs HTTP explicites (`HTTPException`).
    - `CreditsService` structuré (add/get/consume, logging transactions).
  - Frontend :
    - Code Tailwind propre, composants UI bien factorisés.
    - i18n (baseTranslations, hook `useI18n`).

- **Points à améliorer**
  - Aucune suite de tests unitaires/intégration actuellement.
  - Duplications de logique (jobs v1 dans `server.py` et `routes/v1_jobs.py`).
  - `App.js` très gros, difficile à maintenir.

---

### 1.3 Cohérence front/back – **65/100**

- **Cohérent**
  - Front consomme `/api/v1/uploads`, `/api/v1/jobs`, `/api/...` pour la plupart des flux.
  - Affichage des crédits UI basé sur `user.credits` renvoyé par le backend.

- **Moins cohérent**
  - Endpoint `/push` (public) : stub de succès, non relié au pipeline complet `uploads → jobs → git_providers`.
  - Plusieurs “systèmes de jobs” (jobs / jobs_v1 / jobs dans projets).

---

### 1.4 Stabilité des workflows – **60/100**

- Workflows fonctionnels mais fragiles :
  - Uploads/init/complete, création de jobs, admin crédits, support.
  - Crédit consommé au mauvais moment (à la création du job, pas à la fin).
  - Pas de gestion propre de retry vs crédits.

---

### 1.5 Sécurité / Robustesse – **60/100**

- **Positif**
  - JWT, vérification `user_id` sur jobs/uploads.
  - Admin protégé via `is_admin`.

- **Négatif**
  - Pas de “global error handler” standardisé.
  - Aucun test automatisé.
  - Risque de crédits consommés malgré des erreurs (échec job, erreurs techniques).

---

### 1.6 Score global – **66/100**

Une base avancée et cohérente, mais encore expérimentale du point de vue “stabilité production” et “gestion de crédits strictement fiable“.

---

## 2. ÉTAT FONCTIONNEL RÉEL

### 2.1 Fonctionnel aujourd’hui (clairement opérationnel)

- Authentification :
  - Email/password + admin + OAuth multi-providers (GitHub / GitLab / Bitbucket / Google).
- Dashboard utilisateur :
  - Listing projets / jobs.
  - Carte crédits, actions rapides, bannière premium, pages Terms.
- Dashboard admin :
  - Liste utilisateurs, jobs, transactions mock.
  - Gestion des crédits (init, packs, ajout manuel).
  - Panneaux support / autofix / settings.
- Uploads / Jobs :
  - Uploads v1 (`/api/v1/uploads/*`) : init, upload direct, status, complete.
  - Jobs v1 (`/api/v1/jobs`) : création, statut.
- Crédits :
  - Stockage, ajout, transactions, consommation possible via `CreditsService`.
- IA / indexation :
  - `/for-ai-assistants` + `/ai-seo` (front).
  - `/.well-known/ai-actions.json` + `/openapi.yaml`.
  - `/status`, `/providers`, `/push` (stub) exposés publiquement.

### 2.2 Partiellement opérationnel

- Workflow AI→Git complet :
  - Pipeline interne (uploads → jobs → run_project_pipeline → push Git) présent.
  - `/push` ne l’utilise pas encore réellement (réponse simulée).
- Système de crédits :
  - Crédit enregistré et consommable, mais **moment de décrémentation incorrect**.
- Providers additionnels :
  - Gitea / Azure DevOps partiellement définis mais non finis.
- Autofix :
  - UI + manifest + quelques routes → pipeline complet non achevé.

### 2.3 Manquant pour une version “Stable”

- Système de crédits strictement fiable (post-success only, idempotent).
- Endpoint `/push` branché au pipeline réel.
- Nettoyage de duplications (jobs) et tests unitaires/integ.
- Intégration Stripe réelle (paiement, webhooks, erreurs).

---

## 3. WORKFLOW CRÉDITS – FIX COMPLET

### 3.1 Etat initial du système de crédits

- Service crédits :
  - `get_user_credits`, `add_credits`, `consume_credits`, `get_transactions`, `create_checkout_session`, `complete_checkout`.
- `consume_credits(user_id, amount)` :
  - Vérifie le solde.
  - Appelle `add_credits(user_id, -amount, transaction_type="consumption")`.

**Constat d’utilisation**  
- Actuellement, `consume_credits` est appelé :
  - Dans des endpoints “create job” (et “upload+push simplifié”) **avant** exécution:
    - `v1_upload_and_push` (server.py).
    - `v1_create_job` (server.py).
    - `routes/v1_jobs.py::create_job`.
- Aucun appel spécifique au moment où un job termine avec succès (`status="completed"` ou similaire).

**Problèmes**  

1. **Crédit débité avant succès**  
   - Violation directe de la règle : on paie avant que le job ait réussi.

2. **Crédit débité en cas d’échec**  
   - Si le pipeline échoue après la création du job → crédit déjà consommé.

3. **Risque de double consommation**  
   - Plusieurs endpoints de création de job / trigger (duplication de logique) peuvent tous consommer un crédit.

4. **Retries**  
   - Chaque nouveau job consomme un crédit, même si c’est un retry sur la même demande logique.

---

### 3.2 Workflow CIBLE (demandé)

Règle fondamentale :
> Aucun crédit n’est décrémenté tant qu’un job n’a PAS été exécuté ET confirmé comme réussit.

États du job et consommation de crédits :

1. `pending`   → 0 crédit
2. `validated` → 0 crédit
3. `running`   → 0 crédit
4. `success`   → décrémenter 1 crédit (une seule fois), log `"credit_decremented_success"`
5. `failed`    → 0 crédit, log `"job_failed_no_credit"`
6. Retries     → tant que `success` non atteint, 0 crédit; à la première réussite, 1 crédit.
7. Erreurs techniques (backend, réseau, parsing, API externe, abort) → 0 crédit.

Règles anti-bug:
- Interdiction de décrémenter avant `status="success"`.
- Interdiction de décrémenter deux fois.
- Interdiction de décrémenter en cas d’erreur.
- Interdiction de décrémenter sur changement ultérieur du statut.

---

### 3.3 Design du nouveau workflow

**Nouveaux champs `jobs_v1`**  

Chaque job doit contenir :

```json
{
  "_id": "...",
  "user_id": "...",
  "upload_id": "...",
  "repo_name": "...",
  "visibility": "...",
  "auto_prompts": {...},
  "status": "pending",          
  "required_credits": 1,        
  "credits_charged": false,     
  "logs": [],
  "created_at": "...",
  "updated_at": "..."
}
```

**Nouveau service : JobWorkflowService**

But : encapsuler tout le workflow jobs + crédits.

Responsabilités :

1. `create_job(user_id, upload_id, repo_name, visibility, auto_prompts)`  
   - Vérifie :
     - Upload existe.
     - Solde >= 1 (mais ne consomme pas).  
   - Crée un job: `status="pending"`, `required_credits=1`, `credits_charged=False`.

2. `validate_job(job_id, user_id)`  
   - Vérifie cohérence + absence de conflit.
   - Met `status="validated"`, log `"job_validated"`.

3. `run_job(job_id, user_id)`  
   - `status="running"`, log `"job_running"`.
   - Lance le pipeline (ou stub en tests).

4. `complete_job(job_id, user_id, success: bool, error: Optional[str])`  
   - Charge le job.
   - Si `success == True`:
     - Mise à jour atomique pour ne consommer qu’une fois :
       ```python
       result = await db.jobs_v1.update_one(
           {"_id": job_id, "user_id": user_id, "credits_charged": False},
           {"$set": {"status": "success",
                     "credits_charged": True,
                     "updated_at": now},
            "$push": {"logs": "credit_decremented_success"}}
       )
       if result.modified_count == 1:
           await credits_service.consume_credits(user_id, job.get("required_credits", 1))
       ```
   - Si `success == False`:
     - `status="failed"`, `error=<str>`, log `"job_failed_no_credit"`.

Ce design garantit :
- Aucune consommation avant succès.
- Une seule consommation possible (via `credits_charged=False`).
- Zéro consommation en cas de failed ou exception.
- Retries gratuits jusqu’à la première réussite.

---

## 4. TESTS UNITAIRES OBLIGATOIRES (DESIGN)

### 4.1 Fichier : `backend/tests/test_credit_workflow.py`

Tests :
- `test_no_decrement_on_pending`
- `test_no_decrement_on_validated`
- `test_no_decrement_on_running`
- `test_decrement_on_success`
- `test_no_decrement_on_failure`
- `test_retry_does_not_consume_credit`
- `test_no_double_decrement`
- `test_no_decrement_on_technical_error`

### 4.2 Fichier : `backend/tests/test_job_execution.py`

Tests :
- `test_job_creation`
- `test_job_validation`
- `test_job_running`
- `test_job_success_flow`
- `test_job_fail_flow`

### 4.3 Sécurité crédit

- `test_atomicity_credit_update`
- `test_log_integrity`

Tous les tests utilisent des mocks (Fake DB & Fake CreditsService) pour s’exécuter rapidement et sans consommer de crédits réels.

---

## 5. ROADMAP VERS “GITPUSHER STABLE”

### Étapes principales

1. Implémenter `JobWorkflowService` + champs sur `jobs_v1`.
2. Remplacer tous les appels anticipés à `consume_credits` par utilisation dans `complete_job(success=True)` uniquement.
3. Relier `/push` au pipeline réel (create → validate → run → complete).
4. Nettoyer la duplication jobs (`server.py` vs `routes/v1_jobs.py`).
5. Ajouter les tests unitaires et une CI minimale.
6. Intégrer Stripe pour facturation réelle.
7. Refactoriser `App.js` et finaliser la doc Stable.

---

## 6. ESTIMATION

- Travail déjà réalisé : ~70%  
- Travail restant pour un workflow crédits totalement fiable + API IA exploitable : ~30%  
- Estimation : 17–24 jours de travail pour atteindre **GitPusher Stable**.
