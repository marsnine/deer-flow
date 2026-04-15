"use client";

import { PlusIcon, Trash2Icon } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemTitle,
} from "@/components/ui/item";
import { Switch } from "@/components/ui/switch";
import { useI18n } from "@/core/i18n/hooks";
import {
  useEnableMCPServer,
  useMCPConfig,
  useRemoveMCPServer,
} from "@/core/mcp/hooks";
import type { MCPServerConfig } from "@/core/mcp/types";
import { env } from "@/env";

import { SettingsSection } from "./settings-section";
import { ToolCatalogModal } from "./tool-catalog-modal";

export function ToolSettingsPage() {
  const { t } = useI18n();
  const { config, isLoading, error } = useMCPConfig();
  const [catalogOpen, setCatalogOpen] = useState(false);
  const readOnly = env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true";

  return (
    <SettingsSection
      title={t.settings.tools.title}
      description={t.settings.tools.description}
    >
      <div className="flex flex-col gap-4">
        {!readOnly && (
          <div className="flex justify-end">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setCatalogOpen(true)}
            >
              <PlusIcon />
              Add Tool
            </Button>
          </div>
        )}
        {isLoading ? (
          <div className="text-muted-foreground text-sm">
            {t.common.loading}
          </div>
        ) : error ? (
          <div>Error: {error.message}</div>
        ) : (
          config && (
            <MCPServerList
              servers={config.mcp_servers}
              readOnly={readOnly}
            />
          )
        )}
      </div>
      <ToolCatalogModal open={catalogOpen} onOpenChange={setCatalogOpen} />
    </SettingsSection>
  );
}

function MCPServerList({
  servers,
  readOnly,
}: {
  servers: Record<string, MCPServerConfig>;
  readOnly: boolean;
}) {
  const { mutate: enableMCPServer } = useEnableMCPServer();
  const { mutate: removeMCPServer } = useRemoveMCPServer();

  const entries = Object.entries(servers);
  if (entries.length === 0) {
    return (
      <div className="text-muted-foreground rounded-md border border-dashed p-6 text-center text-sm">
        No MCP tools connected yet. Click &ldquo;Add Tool&rdquo; to connect
        one.
      </div>
    );
  }

  return (
    <div className="flex w-full flex-col gap-4">
      {entries.map(([name, config]) => (
        <Item className="w-full" variant="outline" key={name}>
          <ItemContent>
            <ItemTitle>
              <div className="flex items-center gap-2">
                <div>{name}</div>
              </div>
            </ItemTitle>
            <ItemDescription className="line-clamp-4">
              {config.description}
            </ItemDescription>
          </ItemContent>
          <ItemActions>
            <Switch
              checked={config.enabled}
              disabled={readOnly}
              onCheckedChange={(checked) =>
                enableMCPServer({ serverName: name, enabled: checked })
              }
            />
            {!readOnly && (
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label={`Remove ${name}`}
                onClick={() => {
                  if (
                    window.confirm(`Remove MCP server "${name}"?`)
                  ) {
                    removeMCPServer({ serverName: name });
                  }
                }}
              >
                <Trash2Icon />
              </Button>
            )}
          </ItemActions>
        </Item>
      ))}
    </div>
  );
}
