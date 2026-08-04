import useSWRMutation from "swr/mutation";
import { useState } from "react";
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

export default function App() {
  const [question, setQuestion] = useState("");

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
        <Button className="cursor-pointer">レスポンスリアルタイム表示</Button>
        {promptError && (
          <p className="text-red-500">エラー: {promptError.message}</p>
        )}
      </div>

      <div className="flex flex-col w-[480px] gap-4">
        <Card>
          {isPromptMutating ? (
            <div className="flex justify-center items-center ">
              <Spinner />
            </div>
          ) : (
            <div className="m-6">{promptData?.response}</div>
          )}
        </Card>
      </div>
    </div>
  );
}
