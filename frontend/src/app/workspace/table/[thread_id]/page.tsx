"use client";

import { useParams } from "next/navigation";
import { useCallback, useEffect } from "react";

import { type PromptInputMessage } from "@/components/ai-elements/prompt-input";
import { ThreadContext } from "@/components/workspace/messages/context";
import { TableWorkspace } from "@/components/workspace/table";
import { useThreadSettings } from "@/core/settings";
import { ensureTeableAgent } from "@/core/teable/api";
import { useThreadStream } from "@/core/threads/hooks";

const AGENT_NAME = "teable-agent";

export default function TableThreadPage() {
  const { thread_id: threadId } = useParams<{ thread_id: string }>();
  const [settings] = useThreadSettings(threadId);

  useEffect(() => {
    void ensureTeableAgent();
  }, []);

  const [thread, sendMessage] = useThreadStream({
    threadId,
    context: { ...settings.context, agent_name: AGENT_NAME },
  });

  const handleSubmit = useCallback(
    (message: PromptInputMessage) => {
      void sendMessage(threadId, message, { agent_name: AGENT_NAME });
    },
    [sendMessage, threadId],
  );

  const handleStop = useCallback(async () => {
    await thread.stop();
  }, [thread]);

  return (
    <ThreadContext.Provider value={{ thread }}>
      <TableWorkspace
        threadId={threadId}
        thread={thread}
        isNewThread={false}
        onSubmit={handleSubmit}
        onStop={handleStop}
      />
    </ThreadContext.Provider>
  );
}
