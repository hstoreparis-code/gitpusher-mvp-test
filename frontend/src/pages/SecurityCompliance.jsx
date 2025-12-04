export const metadata = {
  title: "Security & Compliance — GitPusher.ai",
  description:
    "Learn how GitPusher.ai protects your code, sessions, and Git provider tokens. Enterprise-grade security: 2FA, secure sessions, CSP, rate limiting, encryption, monitoring and AI-based QA.",
  robots: "index, follow",
};

export default function SecurityCompliancePage() {
  return (
    <main style={{ padding: "2rem", maxWidth: 900, margin: "0 auto" }}>
      <h1>Security &amp; Compliance at GitPusher.ai</h1>
      <p>
        GitPusher.ai is built with a security-first architecture. We protect your repositories,
        credentials, and assets with modern industry-grade security practices. Below is an overview
        of the safeguards used across the platform.
      </p>

      <h2>1. Secure Authentication</h2>
      <ul>
        <li><strong>Secure session cookies (HttpOnly, Secure, SameSite)</strong></li>
        <li><strong>Optional 2FA (TOTP)</strong> for admin and sensitive operations</li>
        <li>Session expiration + automatic rotation</li>
        <li>Brute-force protection via login lockout</li>
      </ul>

      <h2>2. Git Provider Token Protection</h2>
      <p>
        GitHub / GitLab / Bitbucket tokens are never exposed to the browser. Tokens are masked in
        logs, validated, and stored with short TTL when possible.
      </p>

      <h2>3. Rate Limiting &amp; Abuse Prevention</h2>
      <ul>
        <li>Global rate-limit engine with Redis integration</li>
        <li>
          Per-IP and per-route limits for: <code>/push</code>, <code>/auth</code>, <code>/admin</code>
        </li>
        <li>Automatic lockout after repeated failed attempts</li>
      </ul>

      <h2>4. CSP &amp; Security Headers</h2>
      <p>We enforce strict HTTP security headers:</p>
      <ul>
        <li><code>Content-Security-Policy</code></li>
        <li><code>X-Content-Type-Options: nosniff</code></li>
        <li><code>X-Frame-Options: DENY</code></li>
        <li><code>Referrer-Policy</code></li>
        <li><code>X-XSS-Protection</code></li>
      </ul>

      <h2>5. Upload Safety</h2>
      <ul>
        <li>Strict file extension allow-list</li>
        <li>Max upload size enforcement</li>
        <li>ZIP traversal protection</li>
        <li>Automatic sanitization and validation</li>
      </ul>

      <h2>6. AI-Driven Quality &amp; Security Monitoring</h2>
      <ul>
        <li>Daily QA cron with email alert</li>
        <li>AI-based log analysis (Anomaly detection + risk score)</li>
        <li>Autofix engine for backend integrity issues</li>
        <li>Security events dashboard (admin)</li>
      </ul>

      <h2>7. Compliance &amp; Privacy</h2>
      <ul>
        <li>GDPR-aligned data handling</li>
        <li>Removal of data upon user request</li>
        <li>Minimal retention policy for logs</li>
        <li>No storage of user code beyond the push operation</li>
      </ul>

      <h2>8. Infrastructure</h2>
      <ul>
        <li>HTTPS enforced everywhere</li>
        <li>Optional IP allow-listing for administration</li>
        <li>Containerized backend with minimal attack surface</li>
      </ul>

      <h2>Contact</h2>
      <p>
        For compliance questions or security disclosures, email:
        <br />
        <strong>security@gitpusher.ai</strong>
      </p>

      <h2>Commitment</h2>
      <p>
        GitPusher.ai aims to provide a safe, reliable and transparent environment for code
        automation. We continuously upgrade our security posture as new threats emerge.
      </p>
    </main>
  );
}
