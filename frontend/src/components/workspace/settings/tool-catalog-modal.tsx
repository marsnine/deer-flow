"use client";

import { ArrowLeftIcon, ExternalLinkIcon, PlusIcon } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useAddMCPServer, useMCPConfig } from "@/core/mcp/hooks";
import { MCP_PRESETS, type McpPreset } from "@/core/mcp/presets";

type Step = "catalog" | "form";

export function ToolCatalogModal({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [step, setStep] = useState<Step>("catalog");
  const [preset, setPreset] = useState<McpPreset | null>(null);

  function handleOpenChange(next: boolean) {
    if (!next) {
      setStep("catalog");
      setPreset(null);
    }
    onOpenChange(next);
  }

  function handleSelectPreset(next: McpPreset) {
    setPreset(next);
    setStep("form");
  }

  function handleBack() {
    setStep("catalog");
    setPreset(null);
  }

  function handleSuccess() {
    handleOpenChange(false);
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-xl">
        {step === "catalog" ? (
          <CatalogStep onSelect={handleSelectPreset} />
        ) : preset ? (
          <FormStep
            preset={preset}
            onBack={handleBack}
            onSuccess={handleSuccess}
          />
        ) : null}
      </DialogContent>
    </Dialog>
  );
}

function CatalogStep({ onSelect }: { onSelect: (preset: McpPreset) => void }) {
  const { config } = useMCPConfig();
  const existing = new Set(Object.keys(config?.mcp_servers ?? {}));

  return (
    <>
      <DialogHeader>
        <DialogTitle>Add MCP Tool</DialogTitle>
        <DialogDescription>
          Pick a tool to connect. The MCP server runs locally and is available
          to your agent right away.
        </DialogDescription>
      </DialogHeader>
      <div className="grid max-h-[60vh] grid-cols-1 gap-2 overflow-y-auto sm:grid-cols-2">
        {MCP_PRESETS.map((preset) => {
          const alreadyAdded = existing.has(preset.id);
          return (
            <button
              key={preset.id}
              type="button"
              onClick={() => onSelect(preset)}
              className="hover:border-primary hover:bg-accent flex flex-col items-start gap-1 rounded-md border p-3 text-left transition-colors"
            >
              <div className="flex w-full items-center justify-between">
                <div className="font-medium">{preset.displayName}</div>
                {alreadyAdded && (
                  <span className="text-muted-foreground text-xs">
                    Connected
                  </span>
                )}
              </div>
              <div className="text-muted-foreground line-clamp-2 text-xs">
                {preset.description}
              </div>
            </button>
          );
        })}
      </div>
    </>
  );
}

function FormStep({
  preset,
  onBack,
  onSuccess,
}: {
  preset: McpPreset;
  onBack: () => void;
  onSuccess: () => void;
}) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const { config } = useMCPConfig();
  const addMutation = useAddMCPServer();

  const alreadyAdded = Boolean(config?.mcp_servers[preset.id]);

  function handleChange(name: string, value: string) {
    setValues((prev) => ({ ...prev, [name]: value }));
    setFormError(null);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setFormError(null);
    const missing = preset.fields
      .filter((field) => field.required && !values[field.name]?.trim())
      .map((field) => field.label);
    if (missing.length > 0) {
      setFormError(`Missing required: ${missing.join(", ")}`);
      return;
    }
    if (
      alreadyAdded &&
      !window.confirm(
        `"${preset.displayName}" is already connected. Overwrite the existing configuration?`,
      )
    ) {
      return;
    }
    try {
      const serverConfig = preset.toServerConfig(values);
      await addMutation.mutateAsync({
        serverName: preset.id,
        serverConfig,
      });
      onSuccess();
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : "Failed to save server",
      );
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <DialogHeader>
        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            onClick={onBack}
            aria-label="Back to catalog"
          >
            <ArrowLeftIcon />
          </Button>
          <DialogTitle>Connect {preset.displayName}</DialogTitle>
        </div>
        <DialogDescription>{preset.description}</DialogDescription>
      </DialogHeader>
      <div className="flex flex-col gap-4 py-2">
        {preset.fields.map((field) => (
          <div key={field.name} className="flex flex-col gap-1.5">
            <label
              htmlFor={`preset-field-${field.name}`}
              className="text-sm font-medium"
            >
              {field.label}
              {field.required && (
                <span className="text-destructive ml-0.5">*</span>
              )}
            </label>
            <Input
              id={`preset-field-${field.name}`}
              type={field.type === "password" ? "password" : "text"}
              placeholder={field.placeholder}
              value={values[field.name] ?? ""}
              onChange={(event) => handleChange(field.name, event.target.value)}
              autoComplete="off"
              spellCheck={false}
            />
            {field.description && (
              <p className="text-muted-foreground text-xs">
                {field.description}
              </p>
            )}
          </div>
        ))}
        {preset.docsUrl && (
          <a
            href={preset.docsUrl}
            target="_blank"
            rel="noreferrer"
            className="text-primary inline-flex items-center gap-1 text-xs hover:underline"
          >
            <ExternalLinkIcon className="size-3" />
            How to get credentials
          </a>
        )}
        {formError && (
          <div className="text-destructive text-sm">{formError}</div>
        )}
      </div>
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onBack}>
          Cancel
        </Button>
        <Button type="submit" disabled={addMutation.isPending}>
          <PlusIcon />
          {addMutation.isPending ? "Saving..." : "Save"}
        </Button>
      </DialogFooter>
    </form>
  );
}
