 # WorkOS MCP
```bash
import { DocsAccordionHydrator } from "../../components/docs-accordion-hydrator";
import { DocsAccordion } from "../../components/docs-accordion";
import { CopyablePrompt } from "../../components/copyable-prompt";
```
## Overview

The WorkOS MCP server lets MCP-compatible AI agents act on your WorkOS workspace using the [Model Context Protocol](https://modelcontextprotocol.io/). Once connected, your agent can read and change the same dashboard data you can (managing organizations, connections, users, branding, and more) by calling the WorkOS API on your behalf.

The MCP server acts as **you**: it inherits your dashboard role and can only do what your account is allowed to do. See [Permissions](#permissions) for details.

## Connect a client

Every client connects over streamable HTTP and authenticates with OAuth using [WorkOS Connect](https://workos.com/docs/authkit/connect). The first time you connect, your client opens a WorkOS consent screen where you sign in and approve access. After you approve, the agent is connected as your account.

![WorkOS MCP OAuth consent screen](https://images.workoscdn.com/images/856aa389-6e6d-4262-a16a-008369ed3bc3.png?auto=format\&fit=clip\&q=80)

Pick your client below for setup steps.

     <DocsAccordion.Header as="h3">Antigravity</DocsAccordion.Header>

Open the MCP settings and add a new server with the URL `https://mcp.workos.com/mcp`, or add it to the MCP config directly:

```json title="MCP config"
{
  "mcpServers": {
    "workos": {
      "serverUrl": "https://mcp.workos.com/mcp"
    }
  }
}
```

Complete the OAuth consent when prompted to finish connecting.

<DocsAccordion.Header as="h3">ChatGPT</DocsAccordion.Header>

1. Open **Settings â†’ Connectors** (available on ChatGPT Pro, Business, and Enterprise).
2. Click **Add custom connector** (you may need to enable developer mode first).
3. Name it `WorkOS` and enter the MCP server URL `https://mcp.workos.com/mcp`.
4. Complete the OAuth consent to finish connecting.

       <DocsAccordion.Header as="h3">Claude Code</DocsAccordion.Header>

Run the following, then complete the OAuth consent in your browser to finish connecting:

```bash title="Terminal"
claude mcp add --transport http workos https://mcp.workos.com/mcp
```

Use `/mcp` inside Claude Code to check the connection status or sign in again.

    <DocsAccordion.Header as="h3">Claude Desktop</DocsAccordion.Header>

1. Open **Settings â†’ Connectors**.
2. Click **Add custom connector**.
3. Name it `WorkOS` and enter the URL `https://mcp.workos.com/mcp`.
4. Click **Add**, then **Connect** and complete the OAuth consent to finish connecting.

<DocsAccordion.Header as="h3">Codex CLI</DocsAccordion.Header>

Add the server to `~/.codex/config.toml`:

```toml title="~/.codex/config.toml"
[mcp_servers.workos]
url = "https://mcp.workos.com/mcp"
```

Restart Codex and complete the OAuth consent to finish connecting.

    <DocsAccordion.Header as="h3">Cursor</DocsAccordion.Header>

Add the server to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per project):

```json title="mcp.json"
{
  "mcpServers": {
    "workos": {
      "url": "https://mcp.workos.com/mcp"
    }
  }
}
```

Open **Settings â†’ MCP**, then click **Login** next to the WorkOS server and complete the OAuth consent to finish connecting.

<DocsAccordion.Header as="h3">Factory</DocsAccordion.Header>

Add the server to your Factory MCP config (`~/.factory/mcp.json`):

```json title="mcp.json"
{
  "mcpServers": {
    "workos": {
      "type": "http",
      "url": "https://mcp.workos.com/mcp"
    }
  }
}
```

Complete the OAuth consent when prompted to finish connecting.

<DocsAccordion.Header as="h3">Goose</DocsAccordion.Header>

Run `>_goose configure`, choose **Add Extension â†’ Remote Extension (Streaming HTTP)**, and enter the URL `https://mcp.workos.com/mcp`. Complete the OAuth consent when prompted to finish connecting.

      <DocsAccordion.Header as="h3">OpenCode</DocsAccordion.Header>

Add the server to your `opencode.json`:

```json title="opencode.json"
{
  "mcp": {
    "workos": {
      "type": "remote",
      "url": "https://mcp.workos.com/mcp",
      "enabled": true
    }
  }
}
```

Complete the OAuth consent when prompted to finish connecting.

    <DocsAccordion.Header as="h3">VS Code</DocsAccordion.Header>

Add the server to `>_.vscode/mcp.json`:

```json title=".vscode/mcp.json"
{
  "servers": {
    "workos": {
      "type": "http",
      "url": "https://mcp.workos.com/mcp"
    }
  }
}
```

Start the server from the `mcp.json` editor (or run **MCP: List Servers** from the Command Palette) and complete the OAuth consent to finish connecting.

    <DocsAccordion.Header as="h3">Windsurf</DocsAccordion.Header>

> Add the server to `~/.codeium/windsurf/mcp_config.json`:
```json title="mcp_config.json"
{
  "mcpServers": {
    "workos": {
      "serverUrl": "https://mcp.workos.com/mcp"
    }
  }
}
```

Reload the server list in the Windsurf MCP settings, then complete the OAuth consent to finish connecting.

    <DocsAccordion.Header as="h3">Zed</DocsAccordion.Header>

Add the server to your Zed `settings.json` (**Zed â†’ Settings â†’ Open Settings**):
```json title="settings.json"
{
  "context_servers": {
    "workos": {
      "source": "custom",
      "url": "https://mcp.workos.com/mcp"
    }
  }
}
```

Complete the OAuth consent when prompted to finish connecting.

    <DocsAccordion.Header as="h3">Other</DocsAccordion.Header>

For any other MCP client, add a remote MCP server using the URL `https://mcp.workos.com/mcp`. The client will open the WorkOS consent screen so you can sign in and approve access. Complete the OAuth consent to finish connecting.

## Permissions

The MCP server never grants more access than you already have.

> ### Role inheritance

When you connect, the agent authenticates as your dashboard account and assumes your exact role and permissions. Every operation runs through the same access controls that govern the dashboard, so the agent can only read and change what you can. A member without admin rights can't use the agent to perform admin-only actions, and a read-only role can't make any changes at all.

### Environment scope

The agent works against one environment at a time, so it can't accidentally change the wrong one. It defaults to a sandbox environment and only operates on production when you direct it to. Switching to production never escalates your access. The agent can only reach environments you already have access to in the dashboard, and your team's admins can block production entirely.

### Destructive confirmation

Irreversible operations, like deleting an organization, connection, or directory, aren't executed on the first attempt. Instead, the agent receives a description of exactly what the operation will destroy and must explicitly confirm before it runs. This gives you a chance to review the consequences, so a single ambiguous prompt can't wipe out data.

### Secrets

Values like API keys and client secrets are stripped from responses before they ever reach the agent, so they can't leak into its context or be echoed back in a chat transcript. Stripping only applies to returned values, so the agent can still set a secret value you provide without being able to read existing ones back.

### Admin controls

Team admins can restrict or completely disable MCP access for the whole team from the team authentication settings page. Three settings can be toggled independently, and all are enabled by default:

- **Enable**: Allow this team to access the WorkOS dashboard over MCP. Turning this off disables MCP for the team entirely, which also disables the two settings below.

- **Allow production access**: Allow agents to access production environments. When off, MCP can only reach sandbox environments. This never escalates anyone's permissions: agents can still only reach production for members who already have production access in the dashboard.

- **Allow write access**: Allow agents to perform write operations. When off, MCP is restricted to read-only operations.

![WorkOS MCP admin controls](https://images.workoscdn.com/images/88c0d427-131b-4cbc-935f-7f0ea68b1f90.png?auto=format\&fit=clip\&q=80)

## Example prompts

Connect an agent and describe what you want in plain language. The agent discovers the right operations and runs them for you. Here are a few examples.

**Brand your sign-in page from a screenshot**

Here's a screenshot of our marketing site. Make our AuthKit sign-in page match its overall aesthetic.

**Debug a sign-in problem**

Help me understand why `org_123` is having trouble signing in with SSO.

**Onboard a new customer**

Set up a new organization for Acme Corp and invite everyone in `acme_employees.csv`.

**Understand your users**

Show me recent suspicious sign-in attempts and where they came from.

**Manage a user**

Invite `email@examples.com` to `org_123` as an admin.

**Audit your configuration**

List every organization with a draft SSO connection, and flag any directories that haven't synced in 24 hours.

**Stream audit logs**

Set up a Datadog audit log stream for our production environment.

These are just starting points. Try to give agents tasks that you typically do in the dashboard.

## Limitations

Some dashboard capabilities are intentionally unavailable over MCP.

- **No impersonation.** The dashboard's user impersonation isn't exposed to agents, and mutations are blocked on impersonated sessions. An agent always acts as you. It can't act as one of your users.

- **Not every dashboard action.** The agent works with the operations WorkOS has enabled for MCP (managing organizations, connections, users, branding, and more), but the most sensitive actions are intentionally left out. It can't change the MCP access settings that govern its own access, mint or rotate credentials such as API keys, OAuth client secrets, and signing certificates, or delete your WorkOS team.

- **One team at a time.** The agent is scoped to the team you authenticate with. It can't read or change resources belonging to another team.
