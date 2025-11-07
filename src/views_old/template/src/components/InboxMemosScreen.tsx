import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Separator } from "./ui/separator";
import { Progress } from "./ui/progress";
import { Memo, Task, Tag } from "../App";
import { Sparkles, Check, X, Edit2, Plus, Trash2, Inbox, Lightbulb, Loader2, AlertCircle } from "lucide-react";

type InboxMemosScreenProps = {
  memos: Memo[];
  tasks: Task[];
  tags: Tag[];
  navigateTo: (screen: string, itemId?: string) => void;
  onMemoApprove: (memoId: string, generatedTasks: Task[]) => void;
  onMemoMarkAsIdea: (memoId: string) => void;
  onRequestAI: (memoId: string) => void;
};

export function InboxMemosScreen({
  memos,
  tags,
  navigateTo,
  onMemoApprove,
  onMemoMarkAsIdea,
  onRequestAI,
}: InboxMemosScreenProps) {
  const [selectedMemo, setSelectedMemo] = useState<Memo | null>(
    memos.length > 0 ? memos[0] : null
  );
  const [generatedTasks, setGeneratedTasks] = useState<Partial<Task>[]>([
    {
      id: `task-${Date.now()}-1`,
      title: "UIコンポーネントの実装",
      description: "新しい機能のUIコンポーネントを実装する",
      status: "todo",
      tags: ["development"],
      isRecurring: false,
      createdAt: new Date(),
    },
    {
      id: `task-${Date.now()}-2`,
      title: "パフォーマンス最適化の調査",
      description: "現在のパフォーマンスボトルネックを調査する",
      status: "todo",
      tags: ["development"],
      isRecurring: false,
      createdAt: new Date(),
    },
  ]);
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);

  const handleApprove = () => {
    if (!selectedMemo) return;
    onMemoApprove(
      selectedMemo.id,
      generatedTasks.map((t) => ({
        ...t,
        memoId: selectedMemo.id,
      })) as Task[]
    );
    const nextMemo = memos.find((m) => m.id !== selectedMemo.id);
    setSelectedMemo(nextMemo || null);
  };

  const handleMarkAsIdea = () => {
    if (!selectedMemo) return;
    onMemoMarkAsIdea(selectedMemo.id);
    const nextMemo = memos.find((m) => m.id !== selectedMemo.id);
    setSelectedMemo(nextMemo || null);
  };

  const handleRequestAI = () => {
    if (!selectedMemo) return;
    onRequestAI(selectedMemo.id);
  };

  const handleTaskEdit = (taskId: string, field: string, value: any) => {
    setGeneratedTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, [field]: value } : t))
    );
  };

  const handleAddTask = () => {
    const newTask: Partial<Task> = {
      id: `task-${Date.now()}`,
      title: "",
      description: "",
      status: "todo",
      tags: [],
      isRecurring: false,
      createdAt: new Date(),
    };
    setGeneratedTasks((prev) => [...prev, newTask]);
    setEditingTaskId(newTask.id!);
  };

  const handleRemoveTask = (taskId: string) => {
    setGeneratedTasks((prev) => prev.filter((t) => t.id !== taskId));
  };

  const getAIStatusBadge = (memo: Memo) => {
    switch (memo.aiSuggestionStatus) {
      case "not_requested":
        return <Badge variant="outline">AI未実行</Badge>;
      case "pending":
        return (
          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
            <Loader2 className="size-3 mr-1 animate-spin" />
            AI処理中
          </Badge>
        );
      case "available":
        return (
          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-300">
            <Sparkles className="size-3 mr-1" />
            AI提案あり
          </Badge>
        );
      case "reviewed":
        return <Badge variant="secondary">確認済み</Badge>;
      case "failed":
        return (
          <Badge variant="destructive">
            <AlertCircle className="size-3 mr-1" />
            AI失敗
          </Badge>
        );
    }
  };

  if (memos.length === 0) {
    return (
      <div className="p-8">
        <div>
          <h1>Inboxメモ</h1>
          <p className="text-neutral-600 mt-2">整理されていないメモ</p>
        </div>
        <Card className="mt-6">
          <CardContent className="py-12">
            <div className="text-center">
              <Inbox className="size-12 text-neutral-300 mx-auto mb-4" />
              <p className="text-neutral-500">Inboxは空です</p>
              <p className="text-sm text-neutral-400 mt-2">
                右下のボタンから新しいメモを作成できます
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1>Inboxメモ</h1>
        <p className="text-neutral-600 mt-2">整理されていないメモ ({memos.length}件)</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* メモ一覧 */}
        <div className="space-y-3">
          {memos.map((memo) => (
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
                <div className="flex items-start gap-2">
                  <Inbox className="size-4 text-slate-900 mt-1 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-base truncate">{memo.title}</CardTitle>
                    <CardDescription className="text-xs mt-1">
                      {memo.createdAt.toLocaleDateString('ja-JP')}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0 space-y-2">
                <p className="text-sm text-neutral-600 line-clamp-2">{memo.content}</p>
                <div>{getAIStatusBadge(memo)}</div>
                <div className="flex gap-1">
                  {memo.tags.map((tagName) => {
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
              </CardContent>
            </Card>
          ))}
        </div>

        {/* 選択されたメモとAI生成タスク */}
        {selectedMemo && (
          <div className="lg:col-span-2 space-y-4">
            {/* メモ詳細 */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>{selectedMemo.title}</CardTitle>
                  {getAIStatusBadge(selectedMemo)}
                </div>
                <CardDescription>
                  {selectedMemo.createdAt.toLocaleDateString('ja-JP')} 作成
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <Label>メモ内容</Label>
                    <p className="text-sm mt-2 p-3 bg-neutral-50 rounded-lg border">
                      {selectedMemo.content}
                    </p>
                  </div>
                  {selectedMemo.tags.length > 0 && (
                    <div className="flex gap-2">
                      {selectedMemo.tags.map((tagName) => {
                        const tag = tags.find((t) => t.name === tagName);
                        return (
                          <Badge
                            key={tagName}
                            variant="outline"
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
                  )}
                </div>
              </CardContent>
            </Card>

            {/* AI提案のステータスに応じた表示 */}
            {selectedMemo.aiSuggestionStatus === "not_requested" && (
              <Card className="border-blue-200 bg-blue-50">
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Sparkles className="size-5 text-blue-600" />
                    AIタスク生成
                  </CardTitle>
                  <CardDescription>
                    このメモからタスクを自動生成できます
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button onClick={handleRequestAI} className="w-full">
                    <Sparkles className="size-4 mr-2" />
                    AIにタスクを生成させる
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleMarkAsIdea}
                    className="w-full"
                  >
                    <Lightbulb className="size-4 mr-2" />
                    アイデアとしてマーク（タスク化しない）
                  </Button>
                </CardContent>
              </Card>
            )}

            {selectedMemo.aiSuggestionStatus === "pending" && (
              <Card className="border-blue-200 bg-blue-50">
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Loader2 className="size-5 text-blue-600 animate-spin" />
                    AI処理中
                  </CardTitle>
                  <CardDescription>
                    メモの内容からタスクを生成しています...
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Progress value={66} className="h-2" />
                </CardContent>
              </Card>
            )}

            {selectedMemo.aiSuggestionStatus === "available" && (
              <>
                {/* AI生成完了の表示 */}
                <Card className="border-green-200 bg-green-50">
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <Sparkles className="size-5 text-green-600" />
                      AI生成タスク
                    </CardTitle>
                    <CardDescription>
                      メモの内容から{generatedTasks.length}件のタスクが生成されました
                    </CardDescription>
                  </CardHeader>
                </Card>

                {/* 生成されたタスク */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base">生成されたタスク</CardTitle>
                      <Button size="sm" variant="outline" onClick={handleAddTask}>
                        <Plus className="size-4 mr-1" />
                        タスク追加
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {generatedTasks.map((task) => (
                        <div key={task.id} className="p-4 border rounded-lg bg-white space-y-3">
                          {editingTaskId === task.id ? (
                            <>
                              <div>
                                <Label>タイトル</Label>
                                <Input
                                  value={task.title}
                                  onChange={(e) =>
                                    handleTaskEdit(task.id!, "title", e.target.value)
                                  }
                                  className="mt-1"
                                />
                              </div>
                              <div>
                                <Label>説明</Label>
                                <Textarea
                                  value={task.description}
                                  onChange={(e) =>
                                    handleTaskEdit(task.id!, "description", e.target.value)
                                  }
                                  className="mt-1"
                                  rows={3}
                                />
                              </div>
                              <div className="flex gap-2">
                                <Button
                                  size="sm"
                                  onClick={() => setEditingTaskId(null)}
                                >
                                  完了
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => handleRemoveTask(task.id!)}
                                >
                                  <Trash2 className="size-4 mr-1" />
                                  削除
                                </Button>
                              </div>
                            </>
                          ) : (
                            <>
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2">
                                    <span>{task.title}</span>
                                  </div>
                                  <p className="text-neutral-600 text-sm mt-1">
                                    {task.description}
                                  </p>
                                </div>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => setEditingTaskId(task.id!)}
                                >
                                  <Edit2 className="size-4" />
                                </Button>
                              </div>
                            </>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Separator />

                {/* アクションボタン */}
                <div className="flex gap-3 justify-between">
                  <Button variant="outline" onClick={handleMarkAsIdea}>
                    <Lightbulb className="size-4 mr-1" />
                    アイデアとしてマーク
                  </Button>
                  <Button onClick={handleApprove}>
                    <Check className="size-4 mr-1" />
                    タスクを承認してアクティブへ
                  </Button>
                </div>
              </>
            )}

            {selectedMemo.aiSuggestionStatus === "failed" && (
              <Card className="border-red-200 bg-red-50">
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <AlertCircle className="size-5 text-red-600" />
                    AI処理失敗
                  </CardTitle>
                  <CardDescription>
                    タスクの生成に失敗しました。もう一度お試しください。
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button onClick={handleRequestAI} variant="outline" className="w-full">
                    <Sparkles className="size-4 mr-2" />
                    再試行
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleMarkAsIdea}
                    className="w-full"
                  >
                    <Lightbulb className="size-4 mr-2" />
                    アイデアとしてマーク
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
}