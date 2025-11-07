import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Memo, Task, Tag } from "../App";
import { Search, ExternalLink, Calendar } from "lucide-react";

type MemoHistoryScreenProps = {
  memos: Memo[];
  tasks: Task[];
  tags: Tag[];
  navigateTo: (screen: string, itemId?: string) => void;
  selectedMemoId?: string | null;
};

export function MemoHistoryScreen({
  memos,
  tasks,
  tags,
  navigateTo,
  selectedMemoId,
}: MemoHistoryScreenProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedMemo, setSelectedMemo] = useState<Memo | null>(
    selectedMemoId ? memos.find((m) => m.id === selectedMemoId) || null : null
  );

  const filteredMemos = memos.filter(
    (memo) =>
      memo.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      memo.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getLinkedTasks = (memo: Memo) => {
    return tasks.filter((t) => t.memoId === memo.id);
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1>メモ履歴</h1>
        <p className="text-neutral-600 mt-2">
          タスクが生成されたメモの履歴 ({memos.length}件)
        </p>
      </div>

      {/* 検索バー */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-neutral-400" />
        <Input
          placeholder="メモを検索..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* メモ一覧 */}
        <div className="space-y-3">
          {filteredMemos.length === 0 ? (
            <Card>
              <CardContent className="py-8">
                <p className="text-center text-neutral-500">メモが見つかりません</p>
              </CardContent>
            </Card>
          ) : (
            filteredMemos.map((memo) => {
              const linkedTasks = getLinkedTasks(memo);
              return (
                <Card
                  key={memo.id}
                  className={`cursor-pointer transition-all ${
                    selectedMemo?.id === memo.id
                      ? "border-blue-500 shadow-md"
                      : "hover:border-neutral-300"
                  }`}
                  onClick={() => setSelectedMemo(memo)}
                >
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base">{memo.title}</CardTitle>
                    <CardDescription className="text-xs flex items-center gap-1">
                      <Calendar className="size-3" />
                      {memo.createdAt.toLocaleDateString('ja-JP')}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0 space-y-2">
                    <p className="text-sm text-neutral-600 line-clamp-2">{memo.content}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex gap-1">
                        {memo.tags.slice(0, 2).map((tagName) => {
                          const tag = tags.find((t) => t.name === tagName);
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
                      </div>
                      <div className="text-xs text-neutral-500">
                        {linkedTasks.length} タスク
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })
          )}
        </div>

        {/* メモ詳細 */}
        <div className="lg:col-span-2">
          {selectedMemo ? (
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>{selectedMemo.title}</CardTitle>
                  <CardDescription className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                      <Calendar className="size-3" />
                      {selectedMemo.createdAt.toLocaleDateString('ja-JP')} 作成
                    </span>
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="text-sm text-neutral-500 mb-2">内容</div>
                    <p className="p-3 bg-neutral-50 rounded-lg border">
                      {selectedMemo.content}
                    </p>
                  </div>
                  <div>
                    <div className="text-sm text-neutral-500 mb-2">タグ</div>
                    <div className="flex gap-2">
                      {selectedMemo.tags.map((tagName) => {
                        const tag = tags.find((t) => t.name === tagName);
                        return (
                          <Badge
                            key={tagName}
                            variant="outline"
                            className="cursor-pointer"
                            style={{
                              borderColor: tag?.color,
                              color: tag?.color,
                            }}
                            onClick={() => navigateTo("tags", tag?.id)}
                          >
                            {tagName}
                          </Badge>
                        );
                      })}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* 関連タスク */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">関連タスク</CardTitle>
                  <CardDescription>
                    このメモから生成されたタスク ({getLinkedTasks(selectedMemo).length}件)
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {getLinkedTasks(selectedMemo).length === 0 ? (
                    <p className="text-center text-neutral-500 py-4">
                      関連タスクはありません
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {getLinkedTasks(selectedMemo).map((task) => (
                        <div
                          key={task.id}
                          className="p-3 border rounded-lg hover:border-neutral-300 cursor-pointer transition-colors"
                          onClick={() => navigateTo("tasks", task.id)}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <span>{task.title}</span>
                                {task.status === "completed" && (
                                  <Badge variant="secondary" className="text-xs">
                                    完了
                                  </Badge>
                                )}
                                {task.status === "next" && (
                                  <Badge className="text-xs bg-green-600">
                                    次のアクション
                                  </Badge>
                                )}
                                {task.priority === "high" && (
                                  <Badge variant="destructive" className="text-xs">
                                    高
                                  </Badge>
                                )}
                              </div>
                              <p className="text-neutral-600 text-sm mt-1">
                                {task.description}
                              </p>
                            </div>
                            <Button variant="ghost" size="sm">
                              <ExternalLink className="size-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="py-12">
                <p className="text-center text-neutral-500">
                  メモを選択して詳細を表示
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
