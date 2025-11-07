import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "./ui/tabs";
import { Memo, Tag } from "../App";
import {
  Inbox,
  Sparkles,
  Lightbulb,
  Archive,
  Plus,
  Search,
  FileText,
  Calendar,
  Tag as TagIcon,
  ChevronRight,
} from "lucide-react";

type MemosScreenProps = {
  memos: Memo[];
  tags: Tag[];
  navigateTo: (screen: string, itemId?: string) => void;
  selectedMemoId?: string | null;
  initialTab?: Memo["status"];
  onAISuggestionRequest: (memoId: string) => void;
};

export function MemosScreen({
  memos,
  tags,
  navigateTo,
  selectedMemoId,
  initialTab = "inbox",
  onAISuggestionRequest,
}: MemosScreenProps) {
  const [activeTab, setActiveTab] =
    useState<Memo["status"]>(initialTab);
  const [selectedMemo, setSelectedMemo] = useState<Memo | null>(
    selectedMemoId
      ? memos.find((m) => m.id === selectedMemoId) || null
      : null,
  );
  const [searchQuery, setSearchQuery] = useState("");

  const inboxMemos = memos.filter((m) => m.status === "inbox");
  const activeMemos = memos.filter(
    (m) => m.status === "active",
  );
  const ideaMemos = memos.filter((m) => m.status === "idea");
  const archiveMemos = memos.filter(
    (m) => m.status === "archive",
  );

  const filterMemos = (memosList: Memo[]) => {
    if (!searchQuery) return memosList;
    const query = searchQuery.toLowerCase();
    return memosList.filter(
      (memo) =>
        memo.title.toLowerCase().includes(query) ||
        memo.content.toLowerCase().includes(query) ||
        memo.tags.some((t) => t.toLowerCase().includes(query)),
    );
  };

  const getAISuggestionBadge = (
    status: Memo["aiSuggestionStatus"],
  ) => {
    switch (status) {
      case "available":
        return (
          <Badge
            variant="outline"
            className="bg-blue-50 text-blue-700 border-blue-300"
          >
            AI提案あり
          </Badge>
        );
      case "pending":
        return (
          <Badge
            variant="outline"
            className="bg-slate-100 text-slate-700 border-slate-300"
          >
            AI処理中
          </Badge>
        );
      case "reviewed":
        return (
          <Badge
            variant="outline"
            className="bg-slate-100 text-slate-700 border-slate-300"
          >
            確認済み
          </Badge>
        );
      case "failed":
        return (
          <Badge
            variant="outline"
            className="bg-amber-50 text-amber-700 border-amber-300"
          >
            AI失敗
          </Badge>
        );
      default:
        return null;
    }
  };

  const renderMemoList = (
    memosList: Memo[],
    emptyMessage: string,
  ) => {
    const filteredMemos = filterMemos(memosList);

    if (filteredMemos.length === 0) {
      return (
        <Card>
          <CardContent className="py-12">
            <p className="text-center text-neutral-500">
              {emptyMessage}
            </p>
          </CardContent>
        </Card>
      );
    }

    return (
      <div className="space-y-3">
        {filteredMemos.map((memo) => (
          <Card
            key={memo.id}
            className={`cursor-pointer transition-all hover:shadow-md ${
              selectedMemo?.id === memo.id
                ? "border-blue-500 shadow-md"
                : ""
            }`}
            onClick={() => setSelectedMemo(memo)}
          >
            <CardHeader>
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <CardTitle className="text-base truncate">
                    {memo.title}
                  </CardTitle>
                  <CardDescription className="line-clamp-2 mt-1">
                    {memo.content}
                  </CardDescription>
                </div>
                <ChevronRight
                  className={`size-5 text-neutral-400 transition-transform ${
                    selectedMemo?.id === memo.id
                      ? "rotate-90"
                      : ""
                  }`}
                />
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="flex items-center gap-2 flex-wrap">
                {getAISuggestionBadge(memo.aiSuggestionStatus)}
                {memo.tags.map((tagName) => {
                  const tag = tags.find(
                    (t) => t.name === tagName,
                  );
                  return (
                    <Badge
                      key={tagName}
                      variant="outline"
                      className="text-xs"
                      style={{
                        borderColor: tag?.color,
                        color: tag?.color,
                      }}
                    >
                      {tagName}
                    </Badge>
                  );
                })}
                <span className="text-xs text-neutral-500 ml-auto">
                  {memo.createdAt.toLocaleDateString("ja-JP")}
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col">
      {/* ヘッダー */}
      <div className="p-6 border-b bg-white">
        <div className="flex items-center justify-between">
          <div>
            <h1>メモ</h1>
            <p className="text-neutral-600 mt-1">
              思考とアイデアを記録し、AIでタスクに変換
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* 検索バー */}
            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-neutral-400" />
              <Input
                placeholder="メモを検索..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <Button onClick={() => navigateTo("create-memo")}>
              <Plus className="size-4 mr-2" />
              新しいメモ
            </Button>
          </div>
        </div>
      </div>

      {/* メインコンテンツ */}
      <div className="flex-1 overflow-hidden">
        <Tabs
          value={activeTab}
          onValueChange={(v) =>
            setActiveTab(v as Memo["status"])
          }
          className="h-full flex flex-col"
        >
          <div className="px-6 pt-4 border-b bg-white">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger
                value="inbox"
                className="flex items-center gap-2"
              >
                <Inbox className="size-4" />
                <span>Inbox</span>
                <Badge variant="secondary" className="ml-1">
                  {inboxMemos.length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger
                value="active"
                className="flex items-center gap-2"
              >
                <Sparkles className="size-4" />
                <span>アクティブ</span>
                <Badge variant="secondary" className="ml-1">
                  {activeMemos.length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger
                value="idea"
                className="flex items-center gap-2"
              >
                <Lightbulb className="size-4" />
                <span>アイデア</span>
                <Badge variant="secondary" className="ml-1">
                  {ideaMemos.length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger
                value="archive"
                className="flex items-center gap-2"
              >
                <Archive className="size-4" />
                <span>アーカイブ</span>
                <Badge variant="secondary" className="ml-1">
                  {archiveMemos.length}
                </Badge>
              </TabsTrigger>
            </TabsList>
          </div>

          <div className="flex-1 overflow-hidden">
            <div className="h-full grid grid-cols-1 lg:grid-cols-5 gap-6 p-6">
              {/* 左側：メモリスト */}
              <div className="lg:col-span-2 overflow-y-auto">
                <TabsContent value="inbox" className="mt-0">
                  {renderMemoList(
                    inboxMemos,
                    "Inboxメモはありません",
                  )}
                </TabsContent>

                <TabsContent value="active" className="mt-0">
                  {renderMemoList(
                    activeMemos,
                    "アクティブなメモはありません",
                  )}
                </TabsContent>

                <TabsContent value="idea" className="mt-0">
                  {renderMemoList(
                    ideaMemos,
                    "アイデアメモはありません",
                  )}
                </TabsContent>

                <TabsContent value="archive" className="mt-0">
                  {renderMemoList(
                    archiveMemos,
                    "アーカイブされたメモはありません",
                  )}
                </TabsContent>
              </div>

              {/* 右側：メモ詳細 */}
              <div className="lg:col-span-3 overflow-y-auto">
                {selectedMemo ? (
                  <div className="space-y-4 sticky top-0">
                    <Card>
                      <CardHeader>
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1">
                            <CardTitle>
                              {selectedMemo.title}
                            </CardTitle>
                            <div className="flex items-center gap-2 mt-2">
                              {getAISuggestionBadge(
                                selectedMemo.aiSuggestionStatus,
                              )}
                              <Badge
                                variant="outline"
                                className={
                                  selectedMemo.status ===
                                  "inbox"
                                    ? "bg-yellow-50 text-yellow-700 border-yellow-300"
                                    : selectedMemo.status ===
                                        "active"
                                      ? "bg-blue-50 text-blue-700 border-blue-300"
                                      : selectedMemo.status ===
                                          "idea"
                                        ? "bg-blue-50 text-blue-700 border-blue-300"
                                        : "bg-slate-50 text-slate-700 border-slate-300"
                                }
                              >
                                {selectedMemo.status === "inbox"
                                  ? "INBOX"
                                  : selectedMemo.status ===
                                      "active"
                                    ? "ACTIVE"
                                    : selectedMemo.status ===
                                        "idea"
                                      ? "IDEA"
                                      : "ARCHIVE"}
                              </Badge>
                            </div>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div>
                          <div className="text-sm text-neutral-500 mb-2">
                            内容
                          </div>
                          <div className="prose prose-sm max-w-none whitespace-pre-wrap bg-neutral-50 p-4 rounded-lg">
                            {selectedMemo.content}
                          </div>
                        </div>

                        {selectedMemo.tags.length > 0 && (
                          <div>
                            <div className="text-sm text-neutral-500 mb-2">
                              タグ
                            </div>
                            <div className="flex gap-2 flex-wrap">
                              {selectedMemo.tags.map(
                                (tagName) => {
                                  const tag = tags.find(
                                    (t) => t.name === tagName,
                                  );
                                  return (
                                    <Badge
                                      key={tagName}
                                      style={{
                                        backgroundColor:
                                          tag?.color,
                                      }}
                                    >
                                      {tagName}
                                    </Badge>
                                  );
                                },
                              )}
                            </div>
                          </div>
                        )}

                        <div className="pt-4 border-t">
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <div className="text-neutral-500">
                                作成日
                              </div>
                              <div className="mt-1">
                                {selectedMemo.createdAt.toLocaleDateString(
                                  "ja-JP",
                                )}
                              </div>
                            </div>
                            <div>
                              <div className="text-neutral-500">
                                更新日
                              </div>
                              <div className="mt-1">
                                {selectedMemo.updatedAt.toLocaleDateString(
                                  "ja-JP",
                                )}
                              </div>
                            </div>
                          </div>
                        </div>

                        {selectedMemo.aiSuggestionStatus ===
                          "available" && (
                          <div className="pt-4 border-t">
                            <Button
                              className="w-full"
                              variant="default"
                            >
                              <Sparkles className="size-4 mr-2" />
                              AI提案を確認
                            </Button>
                          </div>
                        )}

                        {selectedMemo.aiSuggestionStatus ===
                          "not_requested" && (
                          <div className="pt-4 border-t">
                            <Button
                              className="w-full"
                              variant="outline"
                              onClick={() =>
                                onAISuggestionRequest(
                                  selectedMemo.id,
                                )
                              }
                            >
                              <Sparkles className="size-4 mr-2" />
                              AIでタスクを生成
                            </Button>
                          </div>
                        )}

                        <div>
                          <Button
                            variant="outline"
                            className="w-full"
                          >
                            編集
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  <Card>
                    <CardContent className="py-12">
                      <div className="text-center text-neutral-500">
                        <FileText className="size-12 mx-auto mb-4 text-neutral-300" />
                        <p>メモを選択して詳細を表示</p>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </div>
        </Tabs>
      </div>
    </div>
  );
}