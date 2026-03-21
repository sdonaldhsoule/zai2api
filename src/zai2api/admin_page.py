from __future__ import annotations

from textwrap import dedent


def render_admin_page() -> str:
    return dedent(
        """
        <!doctype html>
        <html lang="zh-CN">
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>zai2api Control Center</title>
            <style>
              :root {
                color-scheme: dark;
                --bg-0: #090c12;
                --bg-1: rgba(18, 24, 38, 0.72);
                --bg-2: rgba(255, 255, 255, 0.08);
                --bg-3: rgba(255, 255, 255, 0.12);
                --line: rgba(255, 255, 255, 0.12);
                --line-strong: rgba(255, 255, 255, 0.2);
                --text-0: #f3f6fb;
                --text-1: rgba(243, 246, 251, 0.78);
                --text-2: rgba(243, 246, 251, 0.55);
                --accent: #6aa9ff;
                --accent-strong: #87bbff;
                --accent-soft: rgba(106, 169, 255, 0.2);
                --danger: #ff7b7b;
                --success: #78e2b1;
                --warning: #ffd36b;
                --shadow-lg: 0 24px 64px rgba(0, 0, 0, 0.38);
                --shadow-md: 0 12px 32px rgba(0, 0, 0, 0.24);
                --radius-xl: 28px;
                --radius-lg: 22px;
                --radius-md: 16px;
                --radius-sm: 12px;
              }

              * { box-sizing: border-box; }
              html, body { height: 100%; }
              body {
                margin: 0;
                font-family: "Segoe UI Variable Text", "Segoe UI", "Noto Sans SC", system-ui, sans-serif;
                background:
                  radial-gradient(circle at top left, rgba(91, 155, 255, 0.26), transparent 30%),
                  radial-gradient(circle at top right, rgba(102, 217, 255, 0.12), transparent 24%),
                  radial-gradient(circle at bottom left, rgba(119, 120, 255, 0.18), transparent 28%),
                  linear-gradient(180deg, #111522 0%, #090c12 100%);
                color: var(--text-0);
                overflow: hidden;
              }

              body::before {
                content: "";
                position: fixed;
                inset: 0;
                background:
                  linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                  linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
                background-size: 40px 40px;
                mask-image: radial-gradient(circle at center, black 45%, transparent 95%);
                pointer-events: none;
              }

              .shell {
                position: relative;
                display: grid;
                grid-template-columns: 280px minmax(0, 1fr);
                gap: 20px;
                height: 100%;
                padding: 24px;
              }

              .panel {
                background: var(--bg-1);
                border: 1px solid var(--line);
                border-radius: var(--radius-xl);
                box-shadow: var(--shadow-lg);
                backdrop-filter: blur(24px) saturate(150%);
                -webkit-backdrop-filter: blur(24px) saturate(150%);
              }

              .sidebar {
                display: flex;
                flex-direction: column;
                gap: 18px;
                padding: 24px;
              }

              .brand {
                display: grid;
                gap: 10px;
              }

              .brand-badge {
                width: 52px;
                height: 52px;
                border-radius: 18px;
                background: linear-gradient(135deg, rgba(106, 169, 255, 0.9), rgba(110, 236, 255, 0.72));
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.32), 0 18px 28px rgba(48, 104, 185, 0.35);
                display: grid;
                place-items: center;
                font-size: 24px;
              }

              .brand-title { font-size: 24px; font-weight: 700; letter-spacing: 0.01em; }
              .brand-copy { color: var(--text-1); line-height: 1.5; font-size: 14px; }

              .nav-list {
                display: grid;
                gap: 10px;
                margin-top: 8px;
              }

              .nav-button,
              .ghost-button,
              .primary-button,
              .secondary-button {
                border: 1px solid transparent;
                border-radius: 16px;
                background: transparent;
                color: inherit;
                cursor: pointer;
                transition: 180ms ease;
                font: inherit;
              }

              .nav-button {
                display: flex;
                align-items: center;
                justify-content: space-between;
                width: 100%;
                padding: 14px 16px;
                color: var(--text-1);
              }

              .nav-button:hover {
                background: var(--bg-2);
                border-color: var(--line);
                color: var(--text-0);
                transform: translateY(-1px);
              }

              .nav-button.active {
                background: linear-gradient(180deg, rgba(106, 169, 255, 0.22), rgba(106, 169, 255, 0.08));
                border-color: rgba(120, 176, 255, 0.35);
                color: var(--text-0);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.15);
              }

              .nav-meta { color: var(--text-2); font-size: 12px; }

              .sidebar-footer {
                margin-top: auto;
                padding: 18px;
                border: 1px solid var(--line);
                border-radius: var(--radius-lg);
                background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
              }

              .main {
                min-width: 0;
                display: flex;
                flex-direction: column;
                padding: 20px;
                gap: 18px;
              }

              .topbar {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                padding: 12px 16px;
                border-radius: 20px;
                border: 1px solid var(--line);
                background: rgba(255,255,255,0.04);
              }

              .headline {
                display: grid;
                gap: 6px;
              }

              .headline h1 {
                margin: 0;
                font-size: 28px;
                line-height: 1.15;
              }

              .headline p {
                margin: 0;
                color: var(--text-1);
                font-size: 14px;
              }

              .top-actions { display: flex; gap: 10px; align-items: center; }

              .ghost-button,
              .secondary-button,
              .primary-button {
                padding: 12px 16px;
                min-height: 44px;
              }

              .ghost-button,
              .secondary-button {
                border-color: var(--line);
                background: rgba(255,255,255,0.04);
              }

              .ghost-button:hover,
              .secondary-button:hover {
                background: rgba(255,255,255,0.08);
                border-color: var(--line-strong);
              }

              .primary-button {
                background: linear-gradient(180deg, var(--accent-strong), var(--accent));
                color: #071120;
                font-weight: 700;
                box-shadow: 0 12px 24px rgba(76, 142, 238, 0.3);
              }

              .primary-button:hover {
                transform: translateY(-1px);
                box-shadow: 0 16px 28px rgba(76, 142, 238, 0.36);
              }

              .primary-button:disabled,
              .secondary-button:disabled,
              .ghost-button:disabled {
                opacity: 0.56;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
              }

              .content {
                min-height: 0;
                display: grid;
                grid-template-rows: auto auto minmax(0, 1fr);
                gap: 18px;
              }

              .hero {
                display: grid;
                grid-template-columns: minmax(0, 1.4fr) minmax(300px, 0.8fr);
                gap: 18px;
              }

              .hero-card,
              .mini-card,
              .view-card,
              .login-card,
              .toast,
              .inline-card {
                border: 1px solid var(--line);
                background: rgba(255,255,255,0.05);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-md);
              }

              .hero-card {
                padding: 22px;
                display: grid;
                gap: 18px;
              }

              .hero-kicker {
                display: inline-flex;
                width: fit-content;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                border-radius: 999px;
                background: rgba(106, 169, 255, 0.12);
                border: 1px solid rgba(106, 169, 255, 0.2);
                color: var(--accent-strong);
                font-size: 12px;
                letter-spacing: 0.04em;
                text-transform: uppercase;
              }

              .hero-title {
                margin: 0;
                font-size: 34px;
                line-height: 1.08;
                max-width: 14ch;
              }

              .hero-text {
                margin: 0;
                color: var(--text-1);
                line-height: 1.7;
                max-width: 68ch;
              }

              .hero-stats,
              .stats-grid,
              .placeholder-grid {
                display: grid;
                gap: 14px;
              }

              .hero-stats { grid-template-columns: repeat(3, minmax(0, 1fr)); }
              .stats-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
              .placeholder-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }

              .mini-card,
              .inline-card {
                padding: 16px;
                display: grid;
                gap: 8px;
              }

              .metric-label {
                color: var(--text-2);
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.08em;
              }

              .metric-value {
                font-size: 28px;
                font-weight: 700;
              }

              .metric-copy,
              .placeholder-copy,
              .muted-copy,
              .field-hint,
              .login-copy {
                color: var(--text-1);
                line-height: 1.6;
              }

              .view-card {
                min-height: 0;
                padding: 22px;
                display: grid;
                gap: 18px;
              }

              .view-header {
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 16px;
              }

              .view-header h2,
              .login-title {
                margin: 0;
                font-size: 22px;
              }

              .placeholder-tile {
                padding: 18px;
                border-radius: 18px;
                border: 1px solid var(--line);
                background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
                display: grid;
                gap: 10px;
              }

              .status-pill {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                border-radius: 999px;
                border: 1px solid var(--line);
                background: rgba(255,255,255,0.04);
                color: var(--text-1);
                font-size: 13px;
              }

              .status-dot {
                width: 8px;
                height: 8px;
                border-radius: 999px;
                background: var(--warning);
                box-shadow: 0 0 14px currentColor;
              }

              .status-dot.success { background: var(--success); }
              .status-dot.error { background: var(--danger); }

              .login-layer {
                position: fixed;
                inset: 0;
                display: grid;
                place-items: center;
                padding: 24px;
                background: rgba(5, 8, 14, 0.42);
                backdrop-filter: blur(18px);
                z-index: 30;
              }

              .login-card {
                width: min(100%, 480px);
                padding: 28px;
                background: linear-gradient(180deg, rgba(20, 26, 42, 0.88), rgba(10, 14, 22, 0.9));
                display: grid;
                gap: 18px;
              }

              .field-group {
                display: grid;
                gap: 10px;
              }

              .field-label {
                color: var(--text-1);
                font-size: 13px;
                font-weight: 600;
              }

              .field-input {
                width: 100%;
                min-height: 50px;
                padding: 14px 16px;
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.14);
                background: rgba(255,255,255,0.05);
                color: var(--text-0);
                outline: none;
                transition: 160ms ease;
              }

              .field-input:focus {
                border-color: rgba(135, 187, 255, 0.46);
                box-shadow: 0 0 0 4px rgba(106, 169, 255, 0.16);
              }

              .banner {
                padding: 14px 16px;
                border-radius: 16px;
                border: 1px solid transparent;
                font-size: 14px;
                line-height: 1.5;
              }

              .banner.info {
                background: rgba(106, 169, 255, 0.12);
                border-color: rgba(106, 169, 255, 0.18);
                color: #cfe0ff;
              }

              .banner.warn {
                background: rgba(255, 211, 107, 0.12);
                border-color: rgba(255, 211, 107, 0.18);
                color: #fff0c7;
              }

              .banner.error {
                background: rgba(255, 123, 123, 0.12);
                border-color: rgba(255, 123, 123, 0.18);
                color: #ffd2d2;
              }

              .toast-stack {
                position: fixed;
                right: 24px;
                bottom: 24px;
                display: grid;
                gap: 12px;
                z-index: 40;
              }

              .toast {
                padding: 14px 16px;
                min-width: 280px;
                max-width: 360px;
                border-left: 4px solid var(--accent);
              }

              .toast.success { border-left-color: var(--success); }
              .toast.error { border-left-color: var(--danger); }

              .hidden { display: none !important; }

              @media (max-width: 1080px) {
                body { overflow: auto; }
                .shell {
                  grid-template-columns: 1fr;
                  height: auto;
                  min-height: 100%;
                }
                .hero,
                .stats-grid,
                .hero-stats,
                .placeholder-grid { grid-template-columns: 1fr; }
              }
            </style>
          </head>
          <body>
            <div class="shell">
              <aside class="panel sidebar">
                <div class="brand">
                  <div class="brand-badge">✦</div>
                  <div class="brand-title">zai2api Control</div>
                  <div class="brand-copy">
                    Fluent-inspired operation center for account orchestration,
                    security governance, and runtime visibility.
                  </div>
                </div>

                <nav class="nav-list" id="nav-list"></nav>

                <div class="sidebar-footer">
                  <div class="metric-label">Runtime posture</div>
                  <div class="muted-copy" id="sidebar-posture">
                    Waiting for bootstrap diagnostics.
                  </div>
                </div>
              </aside>

              <main class="panel main">
                <div class="topbar">
                  <div class="headline">
                    <h1 id="headline-title">Preparing control center...</h1>
                    <p id="headline-copy">Synchronizing admin state and security posture.</p>
                  </div>
                  <div class="top-actions">
                    <button class="ghost-button" id="refresh-button">Refresh</button>
                    <button class="secondary-button" id="logout-button">Sign out</button>
                  </div>
                </div>

                <section class="content" id="content-root"></section>
              </main>
            </div>

            <section class="login-layer hidden" id="login-layer">
              <form class="login-card" id="login-form">
                <div>
                  <div class="hero-kicker">Admin Authentication</div>
                </div>
                <div>
                  <h2 class="login-title">Unlock the control plane</h2>
                  <p class="login-copy">
                    Enter the panel password to access account routing, audit signals,
                    and security controls.
                  </p>
                </div>
                <div class="banner info" id="login-hint"></div>
                <div class="field-group">
                  <label class="field-label" for="panel-password">Panel password</label>
                  <input class="field-input" id="panel-password" type="password" autocomplete="current-password" />
                  <div class="field-hint">If no env or database password is configured, the active default is <strong>123456</strong>.</div>
                </div>
                <button class="primary-button" id="login-submit" type="submit">Sign in</button>
                <div class="banner error hidden" id="login-error"></div>
              </form>
            </section>

            <div class="toast-stack" id="toast-stack"></div>

            <script>
              const views = [
                { id: 'overview', label: 'Overview', meta: 'Live posture' },
                { id: 'accounts', label: 'Accounts', meta: 'Pool operations' },
                { id: 'security', label: 'Security', meta: 'Passwords & policy' },
                { id: 'logs', label: 'Logs', meta: 'Audit signal' },
              ];

              const state = {
                currentView: 'overview',
                loggedIn: false,
                bootstrap: null,
                isBusy: false,
              };

              const navList = document.getElementById('nav-list');
              const contentRoot = document.getElementById('content-root');
              const loginLayer = document.getElementById('login-layer');
              const loginForm = document.getElementById('login-form');
              const loginSubmit = document.getElementById('login-submit');
              const loginHint = document.getElementById('login-hint');
              const loginError = document.getElementById('login-error');
              const panelPassword = document.getElementById('panel-password');
              const refreshButton = document.getElementById('refresh-button');
              const logoutButton = document.getElementById('logout-button');
              const toastStack = document.getElementById('toast-stack');
              const headlineTitle = document.getElementById('headline-title');
              const headlineCopy = document.getElementById('headline-copy');
              const sidebarPosture = document.getElementById('sidebar-posture');

              function showToast(message, tone = 'info') {
                const node = document.createElement('div');
                node.className = `toast ${tone}`;
                node.textContent = message;
                toastStack.appendChild(node);
                setTimeout(() => {
                  node.style.opacity = '0';
                  node.style.transform = 'translateY(10px)';
                }, 2600);
                setTimeout(() => node.remove(), 3200);
              }

              function setBusy(flag) {
                state.isBusy = flag;
                refreshButton.disabled = flag;
                logoutButton.disabled = flag;
                loginSubmit.disabled = flag;
                loginSubmit.textContent = flag ? 'Signing in...' : 'Sign in';
              }

              function renderNav() {
                navList.innerHTML = views.map((view) => {
                  const active = view.id === state.currentView ? 'active' : '';
                  return `
                    <button class="nav-button ${active}" data-view="${view.id}">
                      <span>${view.label}</span>
                      <span class="nav-meta">${view.meta}</span>
                    </button>
                  `;
                }).join('');
                navList.querySelectorAll('[data-view]').forEach((button) => {
                  button.addEventListener('click', () => {
                    state.currentView = button.dataset.view;
                    render();
                  });
                });
              }

              function metricCard(label, value, copy) {
                return `
                  <article class="mini-card">
                    <div class="metric-label">${label}</div>
                    <div class="metric-value">${value}</div>
                    <div class="metric-copy">${copy}</div>
                  </article>
                `;
              }

              function overviewView() {
                const bootstrap = state.bootstrap || {};
                const accounts = bootstrap.accounts || {};
                const panelPassword = bootstrap.panel_password || {};
                const apiPassword = bootstrap.api_password || {};
                const defaultBanner = panelPassword.default_password_active
                  ? '<div class="banner warn">Panel password is currently using the default fallback <strong>123456</strong>. Change it in the next step for safer administration.</div>'
                  : '';
                return `
                  <section class="hero">
                    <article class="hero-card">
                      <div class="hero-kicker">Operational Snapshot</div>
                      <h2 class="hero-title">Account routing is online and ready for live control.</h2>
                      <p class="hero-text">
                        This shell is intentionally focused on readiness feedback. The next phase will wire the live forms, tables,
                        and streaming log views directly into these sections.
                      </p>
                      ${defaultBanner}
                      <div class="hero-stats">
                        ${metricCard('Persisted accounts', accounts.persisted_total ?? 0, 'Accounts currently stored in SQLite.')}
                        ${metricCard('Enabled accounts', accounts.persisted_enabled ?? 0, 'Healthy accounts available for routing.')}
                        ${metricCard('API auth', apiPassword.enabled ? 'On' : 'Off', apiPassword.enabled ? 'Requests require the configured API password.' : 'Requests are currently open because no API password is active.')}
                      </div>
                    </article>
                    <article class="hero-card">
                      <div class="metric-label">Security posture</div>
                      <div class="status-pill">
                        <span class="status-dot ${apiPassword.enabled ? 'success' : ''}"></span>
                        Panel password source: ${panelPassword.source || 'unknown'}
                      </div>
                      <div class="status-pill">
                        <span class="status-dot ${accounts.using_env_fallback ? '' : 'success'}"></span>
                        ${accounts.using_env_fallback ? 'Using env fallback credentials' : 'Using persisted account pool'}
                      </div>
                      <div class="muted-copy">
                        Account, security, and logs pages are scaffolded below with the same routing model the final UI will use.
                      </div>
                    </article>
                  </section>
                  <section class="stats-grid">
                    ${metricCard('Panel auth source', panelPassword.source || 'unknown', 'Env takes precedence over database and fallback.')}
                    ${metricCard('API password source', apiPassword.source || 'disabled', 'Disabled means /v1 requests currently do not require auth.')}
                    ${metricCard('Env fallback', accounts.using_env_fallback ? 'Yes' : 'No', 'When no persisted account is enabled, env credentials can still route requests.')}
                    ${metricCard('Frontend stage', 'Shell', 'Forms, tables, and live log explorers land in the next UI pass.')}
                  </section>
                `;
              }

              function placeholderView(title, copy, bullets) {
                return `
                  <section class="view-card">
                    <div class="view-header">
                      <div>
                        <h2>${title}</h2>
                        <p class="muted-copy">${copy}</p>
                      </div>
                      <div class="status-pill"><span class="status-dot"></span>Interactive wiring lands next</div>
                    </div>
                    <div class="placeholder-grid">
                      ${bullets.map((bullet) => `
                        <article class="placeholder-tile">
                          <div class="metric-label">Planned interaction</div>
                          <div class="placeholder-copy">${bullet}</div>
                        </article>
                      `).join('')}
                    </div>
                  </section>
                `;
              }

              function renderContent() {
                if (state.currentView === 'overview') {
                  return overviewView();
                }
                if (state.currentView === 'accounts') {
                  return placeholderView(
                    'Account operations',
                    'Add JWT credentials, inspect pool health, and manually repair disabled accounts from one place.',
                    [
                      'JWT submission with inline validation, optimistic loading, and success / failure toasts.',
                      'Account cards with state badges, failure counters, and manual check actions.',
                      'Round-robin pool summary and env-fallback visibility for routing confidence.',
                      'Toggle buttons for enable / disable with immediate state reflection.',
                    ],
                  );
                }
                if (state.currentView === 'security') {
                  return placeholderView(
                    'Security controls',
                    'Update panel access and API password policy with clear confirmation feedback.',
                    [
                      'Change panel password with validation and safe success feedback.',
                      'Enable, rotate, or disable API password enforcement.',
                      'Show whether settings are overridden by env so the operator is never confused.',
                      'Surface the polling interval and security posture summary in one place.',
                    ],
                  );
                }
                return placeholderView(
                  'Audit log console',
                  'Browse account lifecycle events, security updates, and request-level warnings without leaving the control center.',
                  [
                    'Live log stream with filter chips for category and severity.',
                    'Recent failures pinned at the top for fast incident triage.',
                    'Compact timeline cards tuned for terminal-like readability.',
                    'Refresh and retention controls with subtle progress feedback.',
                  ],
                );
              }

              function render() {
                renderNav();
                const bootstrap = state.bootstrap || {};
                const accounts = bootstrap.accounts || {};
                headlineTitle.textContent = state.loggedIn ? 'Control center online' : 'Authentication required';
                headlineCopy.textContent = state.loggedIn
                  ? 'You are looking at the Fluent shell. Live management workflows will be connected in the next implementation phase.'
                  : 'Sign in to unlock account orchestration, security settings, and audit visibility.';
                sidebarPosture.textContent = state.loggedIn
                  ? `Persisted ${accounts.persisted_enabled ?? 0} / ${accounts.persisted_total ?? 0} accounts. ${accounts.using_env_fallback ? 'Env fallback is active.' : 'Persisted pool is active.'}`
                  : 'Panel is locked. Use the password gate to continue.';
                loginLayer.classList.toggle('hidden', state.loggedIn);
                logoutButton.classList.toggle('hidden', !state.loggedIn);
                contentRoot.innerHTML = state.loggedIn
                  ? renderContent()
                  : `
                    <section class="hero">
                      <article class="hero-card">
                        <div class="hero-kicker">Access control</div>
                        <h2 class="hero-title">This route is protected by the panel password.</h2>
                        <p class="hero-text">
                          Sign in from the acrylic gate to continue. The shell will immediately sync your latest backend posture once authenticated.
                        </p>
                      </article>
                      <article class="hero-card">
                        <div class="metric-label">Current defaults</div>
                        <div class="placeholder-copy">
                          If no env or database value exists, the panel password falls back to <strong>123456</strong> and the API password remains disabled.
                        </div>
                      </article>
                    </section>
                  `;
              }

              async function refreshBootstrap(showToastOnSuccess = false) {
                try {
                  const response = await fetch('/api/admin/bootstrap', { credentials: 'same-origin' });
                  const payload = await response.json();
                  state.bootstrap = payload;
                  state.loggedIn = Boolean(payload.logged_in);
                  loginHint.textContent = payload.panel_password?.default_password_active
                    ? 'Default fallback password is active. Sign in and rotate it as soon as possible.'
                    : 'Use the active panel password to access the admin surface.';
                  render();
                  if (showToastOnSuccess) {
                    showToast('Control plane refreshed.', 'success');
                  }
                } catch (error) {
                  console.error(error);
                  showToast('Failed to refresh bootstrap state.', 'error');
                }
              }

              loginForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                loginError.classList.add('hidden');
                setBusy(true);
                try {
                  const response = await fetch('/api/admin/login', {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: { 'content-type': 'application/json' },
                    body: JSON.stringify({ password: panelPassword.value }),
                  });
                  const payload = await response.json().catch(() => ({}));
                  if (!response.ok) {
                    loginError.textContent = payload.detail || 'Login failed.';
                    loginError.classList.remove('hidden');
                    showToast('Panel authentication failed.', 'error');
                    return;
                  }
                  panelPassword.value = '';
                  showToast('Signed in successfully.', 'success');
                  await refreshBootstrap(false);
                } finally {
                  setBusy(false);
                }
              });

              refreshButton.addEventListener('click', () => refreshBootstrap(true));
              logoutButton.addEventListener('click', async () => {
                setBusy(true);
                try {
                  await fetch('/api/admin/logout', { method: 'POST', credentials: 'same-origin' });
                  state.loggedIn = false;
                  state.currentView = 'overview';
                  showToast('Signed out.', 'success');
                  await refreshBootstrap(false);
                } finally {
                  setBusy(false);
                }
              });

              refreshBootstrap(false);
            </script>
          </body>
        </html>
        """
    ).strip()
