export type MCPTransport = "stdio" | "sse" | "http";

export interface MCPOAuthConfig {
  enabled?: boolean;
  token_url?: string;
  grant_type?: "client_credentials" | "refresh_token" | "authorization_code";
  client_id?: string | null;
  client_secret?: string | null;
  refresh_token?: string | null;
  scope?: string | null;
  audience?: string | null;
  token_field?: string;
  token_type_field?: string;
  expires_in_field?: string;
  default_token_type?: string;
  refresh_skew_seconds?: number;
  extra_token_params?: Record<string, string>;
}

export interface MCPServerConfig {
  enabled: boolean;
  description: string;
  type?: MCPTransport;
  command?: string | null;
  args?: string[];
  env?: Record<string, string>;
  url?: string | null;
  headers?: Record<string, string>;
  oauth?: MCPOAuthConfig | null;
}

export interface MCPConfig {
  mcp_servers: Record<string, MCPServerConfig>;
}
