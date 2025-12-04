import AIMeta from "../components/AIMeta";

export const metadata = {
  title: "GitPusher.ai — For No-Code Builders",
  description:
    "The easiest way for no-code creators to publish projects to GitHub. Upload, push, and generate clean repositories automatically. No Git required.",
  robots: "index, follow",
};

export default function ForNocodeBuildersPage() {
  return (
    <main style={{ padding: '24px', maxWidth: '900px', margin: '0 auto' }}>
      <AIMeta />

      <header>
        <h1>GitPusher.ai — For No-Code Builders</h1>
        <p>
          Publish your no-code projects to GitHub in seconds — no Git, no terminal, no setup.
          GitPusher.ai transforms your exported files, folders, or AI-generated content into clean,
          production-ready repositories.
        </p>
      </header>

      <section>
        <h2>1. Why GitPusher is perfect for No-Code creators</h2>
        <ul>
          <li>No need to install Git or GitHub Desktop.</li>
          <li>No command line required.</li>
          <li>Compatible with Webflow, Bubble, Framer, Glide, Adalo, Notion, Softr, and more.</li>
          <li>Automatically generates README, .gitignore, and first commit.</li>
          <li>Pushes to GitHub, GitLab, Bitbucket, Gitea, and others.</li>
        </ul>
        <p>
          GitHub becomes <strong>accessible to everyone</strong> — even without technical skills.
        </p>
      </section>

      <section>
        <h2>2. No-Code use cases</h2>
        <ul>
          <li>Webflow export → GitHub repo for a developer.</li>
          <li>Bubble export → clean versioned repo.</li>
          <li>Framer project → shared repository for collaboration.</li>
          <li>AI-generated project folder → automatic repository creation.</li>
          <li>ZIP website → deploy-ready Git repository instantly.</li>
        </ul>
      </section>

      <section>
        <h2>3. How GitPusher works</h2>
        <ol>
          <li>Prepare your export or project folder.</li>
          <li>Upload the ZIP or files to GitPusher.ai.</li>
          <li>Select GitHub or another provider.</li>
          <li>GitPusher generates project structure + repo files.</li>
          <li>Your repository is ready in seconds.</li>
        </ol>
      </section>

      <section>
        <h2>4. API example (optional for advanced workflows)</h2>
        <p>
          You don’t need to code anything, but advanced no-code builders can automate pushes using
          Make, Zapier, or custom scripts:
        </p>

        <pre style={{ whiteSpace: 'pre-wrap', background: '#111', color: '#eee', padding: '12px', borderRadius: '8px' }}>
{`POST https://gitpusher.ai/api/v1/push
{
  "provider": "github",
  "source": "zip",
  "repo_name": "nocode-project",
  "visibility": "private",
  "content": "<BASE64_ZIP>"
}`}
        </pre>
      </section>

      <section>
        <h2>5. Popular No-Code integrations</h2>

        <h3>Webflow → GitHub</h3>
        <p>Export → upload → repo created instantly.</p>

        <h3>Bubble → client deliverables</h3>
        <p>Create clean repos for client handoffs.</p>

        <h3>Framer → developer collaboration</h3>
        <p>Turn prototypes into structured repositories.</p>

        <h3>Make / Zapier automation</h3>
        <p>
          Build workflows that export, upload, and push automatically — no manual steps required.
        </p>
      </section>

      <section>
        <h2>6. No-Code FAQ</h2>
        <dl>
          <dt>Do I need Git installed?</dt>
          <dd>No.</dd>

          <dt>Can I create private repositories?</dt>
          <dd>Yes.</dd>

          <dt>Does GitPusher work with Webflow exports?</dt>
          <dd>Perfectly.</dd>

          <dt>Does GitPusher change my code?</dt>
          <dd>No — only adds Git structure (README, .gitignore, commit).</dd>

          <dt>Can I automate everything?</dt>
          <dd>Yes, via the GitPusher API.</dd>
        </dl>
      </section>

      <footer style={{ marginTop: '32px', fontSize: '0.9rem', opacity: 0.8 }}>
        <p>
          GitPusher.ai — the simplest and fastest way for no-code creators to publish projects to
          Git repositories.
        </p>
      </footer>
    </main>
  );
}
