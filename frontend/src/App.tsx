import useSWRMutation from "swr/mutation";
import { Button } from "@/components/ui/button";

type FetchResult = {
  env: string;
  message: string;
};

async function fetchData(url: string): Promise<FetchResult> {
  const response = await fetch(url, { method: "GET" });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return await response.json();
}

export default function App() {
  const { trigger, isMutating, data, error } = useSWRMutation(
    "/api/",
    fetchData,
  );

  return (
    <div className="flex justify-center items-center h-screen">
      <div className="flex flex-col w-[480px] gap-4">
        <Button
          className="cursor-pointer"
          disabled={isMutating}
          onClick={async () => {
            await trigger();
          }}
        >
          {isMutating ? "取得中..." : "fetch"}
        </Button>
        {error && <p className="text-red-500">エラー: {error.message}</p>}
        <ul>
          <li>env: {data?.env}</li>
          <li>message: {data?.message}</li>
        </ul>
      </div>
    </div>
  );
}
