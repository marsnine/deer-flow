import { useQuery } from "@tanstack/react-query";

import {
  fetchTeableBases,
  fetchTeableConfig,
  fetchTeableShareView,
  fetchTeableSpaces,
  fetchTeableTables,
} from "./api";

export function useTeableConfig() {
  return useQuery({
    queryKey: ["teable", "config"],
    queryFn: fetchTeableConfig,
    staleTime: 5 * 60 * 1000,
  });
}

export function useTeableSpaces() {
  return useQuery({
    queryKey: ["teable", "spaces"],
    queryFn: fetchTeableSpaces,
    staleTime: 60 * 1000,
  });
}

export function useTeableBases(spaceId: string | null) {
  return useQuery({
    queryKey: ["teable", "bases", spaceId],
    queryFn: () => fetchTeableBases(spaceId!),
    enabled: !!spaceId,
    staleTime: 60 * 1000,
  });
}

export function useTeableTables(baseId: string | null | undefined) {
  return useQuery({
    queryKey: ["teable", "tables", baseId],
    queryFn: () => fetchTeableTables(baseId!),
    enabled: !!baseId,
    staleTime: 30 * 1000,
  });
}

export function useTeableShareView(tableId: string | null) {
  return useQuery({
    queryKey: ["teable", "share-view", tableId],
    queryFn: () => fetchTeableShareView(tableId!),
    enabled: !!tableId,
    staleTime: 10 * 60 * 1000,
  });
}
