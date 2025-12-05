export const metadata = {
  title: "Sécurité & Conformité — GitPusher.ai",
  description:
    "Découvrez comment GitPusher.ai protège votre code, vos sessions et vos tokens Git. Sécurité de niveau entreprise : 2FA, sessions sécurisées, CSP, rate limiting, chiffrement, monitoring et QA assistée par IA.",
  robots: "index, follow",
};

export default function SecurityComplianceFR() {
  return (
    <main style={{ padding: "2rem", maxWidth: 900, margin: "0 auto" }}>
      <h1>Sécurité &amp; Conformité chez GitPusher.ai</h1>
      <p>
        GitPusher.ai est conçu avec une architecture « security-first ». Nous protégeons vos dépôts,
        vos identifiants et vos actifs avec des pratiques de sécurité modernes de niveau industrie.
        Voici une synthèse des mesures mises en place sur la plateforme.
      </p>

      <h2>1. Authentification sécurisée</h2>
      <ul>
        <li><strong>Cookies de session sécurisés</strong> (HttpOnly, Secure, SameSite)</li>
        <li><strong>2FA (TOTP) en option</strong> pour les admins et opérations sensibles</li>
        <li>Expiration des sessions + rotation automatique</li>
        <li>Protection anti brute-force via verrouillage après échecs répétés</li>
      </ul>

      <h2>2. Protection des tokens Git</h2>
      <p>
        Les tokens GitHub / GitLab / Bitbucket ne sont jamais exposés au navigateur. Les tokens sont
        masqués dans les logs, validés et stockés avec une durée de vie courte quand c&apos;est possible.
      </p>

      <h2>3. Rate limiting &amp; prévention des abus</h2>
      <ul>
        <li>Moteur de rate limit global avec intégration Redis</li>
        <li>
          Limites par IP et par route pour : <code>/push</code>, <code>/auth</code>, <code>/admin</code>
        </li>
        <li>Verrouillage automatique après plusieurs tentatives échouées</li>
      </ul>

      <h2>4. CSP &amp; en-têtes de sécurité</h2>
      <p>Nous appliquons des en-têtes HTTP stricts :</p>
      <ul>
        <li><code>Content-Security-Policy</code></li>
        <li><code>X-Content-Type-Options: nosniff</code></li>
        <li><code>X-Frame-Options: DENY</code></li>
        <li><code>Referrer-Policy</code></li>
        <li><code>X-XSS-Protection</code></li>
      </ul>

      <h2>5. Sécurité des uploads</h2>
      <ul>
        <li>Liste blanche stricte des extensions autorisées</li>
        <li>Limitation de la taille maximale des fichiers</li>
        <li>Protection contre la traversée de répertoires dans les archives ZIP</li>
        <li>Sanitisation et validation systématiques</li>
      </ul>

      <h2>6. Monitoring qualité &amp; sécurité piloté par l&apos;IA</h2>
      <ul>
        <li>Cron QA quotidien avec alertes email</li>
        <li>Analyse de logs assistée par IA (détection d&apos;anomalies + score de risque)</li>
        <li>Moteur d&apos;autofix pour les problèmes d&apos;intégrité backend</li>
        <li>Dashboard de suivi des événements de sécurité (admin)</li>
      </ul>

      <h2>7. Conformité &amp; vie privée</h2>
      <ul>
        <li>Gestion des données alignée sur le RGPD</li>
        <li>Suppression des données sur demande de l&apos;utilisateur</li>
        <li>Politique de rétention minimale pour les logs</li>
        <li>Aucun stockage durable du code utilisateur au-delà de l&apos;opération de push</li>
      </ul>

      <h2>8. Infrastructure</h2>
      <ul>
        <li>HTTPS forcé partout</li>
        <li>Possibilité de liste blanche d&apos;IP pour l&apos;administration</li>
        <li>Backend containerisé avec surface d&apos;attaque minimale</li>
      </ul>

      <h2>Contact</h2>
      <p>
        Pour toute question de conformité ou divulgation de vulnérabilité, contactez :
        <br />
        <strong>security@gitpusher.ai</strong>
      </p>

      <h2>Engagement</h2>
      <p>
        GitPusher.ai vise à offrir un environnement sûr, fiable et transparent pour l&apos;automatisation
        de code. Notre posture de sécurité est continuellement renforcée au fur et à mesure que de
        nouvelles menaces apparaissent.
      </p>
    </main>
  );
}
