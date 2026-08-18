import useSWRMutation from "swr/mutation";
import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";

type FetchResult = {
  env: string;
  message: string;
};

type LlmResponse = {
  response: string;
};

type SseEvent = {
  event: string;
  data: LlmResponse;
};

type Status = "idle" | "streaming" | "done" | "error";
const INITIAL_STATUS: Status = "idle";

async function fetchData(url: string): Promise<FetchResult> {
  const response = await fetch(url, { method: "GET" });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return await response.json();
}

async function generateAnswer(
  url: string,
  { arg }: { arg: { prompt: string } },
): Promise<LlmResponse> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(arg),
  });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return await response.json();
}

function parseSSE(buffer: string) {
  const parts = buffer.split("\n\n");
  const rest = parts.pop() ?? "";

  const events: SseEvent[] = [];
  for (const block of parts) {
    const lines = block.split("\n");
    let eventName = "message";
    const dataLines: string[] = [];

    for (const line of lines) {
      if (line.startsWith(":")) continue;
      if (line.startsWith("event:")) {
        eventName = line.slice("event:".length).trim();
      }
      if (line.startsWith("data:")) {
        dataLines.push(line.slice("data:".length).trim());
      }
    }
    if (dataLines.length === 0) continue;
    events.push({ event: eventName, data: JSON.parse(dataLines.join("\n")) });
  }
  return { events, rest };
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [status, setStatus] = useState(INITIAL_STATUS);

  const abortRef = useRef(null as AbortController | null);

  const {
    trigger: triggerGet,
    isMutating: isGetMutating,
    data: getData,
    error: getError,
  } = useSWRMutation("/api/", fetchData);

  const {
    trigger: triggerPrompt,
    isMutating: isPromptMutating,
    data: promptData,
    error: promptError,
  } = useSWRMutation("/api/prompt", generateAnswer);

  const stream = async (question: string) => {
    setAnswer("");
    setErrorMessage("");
    setStatus("streaming");
    abortRef.current = new AbortController();

    try {
      const response = await fetch("/api/prompt/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: question }),
        signal: abortRef.current.signal,
      });
      if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
      if (!response.body) throw new Error("body がありません");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parsed = parseSSE(buffer);
        buffer = parsed.rest;

        for (const { event, data } of parsed.events) {
          switch (event) {
            case "chunk":
              setAnswer((prev) => prev + data.response);
              break;
            case "done":
              setStatus("done");
              break;
            case "error":
              setErrorMessage(data.response);
              setStatus("error");
              break;
          }
        }
      }
      setQuestion("");
    } catch (e) {
      if (e instanceof DOMException && e.name === "AbortError") {
        setStatus("idle");
      } else {
        setErrorMessage(
          e instanceof Error ? e.message : "不明なエラーが発生しました",
        );
        setStatus("error");
      }
    } finally {
      abortRef.current = null;
    }
  };

  const cancel = () => {
    abortRef.current?.abort();
  };

  return (
    <div className="flex flex-col justify-center items-center h-screen gap-12">
      <div className="flex flex-col w-[480px] gap-4">
        <Button
          className="cursor-pointer"
          disabled={isGetMutating}
          onClick={async () => {
            await triggerGet();
          }}
        >
          {isGetMutating ? "取得中..." : "fetch"}
        </Button>
        {getError && <p className="text-red-500">エラー: {getError.message}</p>}
        <ul>
          <li>env: {getData?.env}</li>
          <li>message: {getData?.message}</li>
        </ul>
      </div>

      <div className="flex flex-col w-[480px] gap-4">
        <Label>質問入力</Label>
        <Textarea
          placeholder="質問内容を入力してください。"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <Button
          className="cursor-pointer"
          disabled={isPromptMutating || !question.trim()}
          onClick={async () => {
            try {
              await triggerPrompt({ prompt: question });
              setQuestion("");
            } catch {}
          }}
        >
          {isPromptMutating ? "生成中..." : "レスポンス一括表示"}
        </Button>
        {promptError && (
          <p className="text-red-500">エラー: {promptError.message}</p>
        )}
        <Card>
          {isPromptMutating ? (
            <div className="flex justify-center items-center ">
              <Spinner />
            </div>
          ) : (
            <div className="m-6">{promptData?.response}</div>
          )}
        </Card>

        {status === "streaming" ? (
          <Button
            className="cursor-pointer"
            variant="destructive"
            onClick={() => cancel()}
          >
            中断
          </Button>
        ) : (
          <Button
            className="cursor-pointer"
            disabled={!question.trim()}
            onClick={() => stream(question)}
          >
            レスポンスリアルタイム表示
          </Button>
        )}
        {errorMessage && <p className="text-red-500">エラー: {errorMessage}</p>}
        <Card>
          <div className="m-6 whitespace-pre-wrap">{answer}</div>
        </Card>
      </div>
    </div>
  );
}
