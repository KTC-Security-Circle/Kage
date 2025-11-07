import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import { Memo } from "../App";
import { PenLine, Sparkles } from "lucide-react";

type CreateMemoDialogProps = {
  onCreateMemo: (memo: Memo) => void;
  onNavigateToProcessing?: () => void;
};

export function CreateMemoDialog({
  onCreateMemo,
  onNavigateToProcessing,
}: CreateMemoDialogProps) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  const handleCreate = () => {
    if (!content.trim()) return;

    const newMemo: Memo = {
      id: `memo-${Date.now()}`,
      title: title.trim() || "無題のメモ",
      content: content.trim(),
      status: "inbox",
      aiSuggestionStatus: "not_requested",
      createdAt: new Date(),
      updatedAt: new Date(),
      tags: [],
      linkedTasks: [],
    };

    onCreateMemo(newMemo);
    setTitle("");
    setContent("");
    setOpen(false);

    // メモ作成後、Inboxメモ画面に遷移
    if (onNavigateToProcessing) {
      setTimeout(() => {
        onNavigateToProcessing();
      }, 100);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Ctrl+Enter または Cmd+Enter で送信
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      handleCreate();
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          size="lg"
          className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg hover:shadow-xl transition-shadow z-50"
        >
          <PenLine className="size-6" />
          <span className="sr-only">新しいメモを作成</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <PenLine className="size-5" />
            新しいメモを作成
          </DialogTitle>
          <DialogDescription>
            メモの内容を入力してください。AIがタスクを自動生成します。
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="memo-title">タイトル（任意）</Label>
            <Input
              id="memo-title"
              placeholder="メモのタイトルを入力..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              onKeyDown={handleKeyDown}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="memo-content">
              内容 <span className="text-red-500">*</span>
            </Label>
            <Textarea
              id="memo-content"
              placeholder="メモの内容を入力してください。例：プロジェクトAの新機能について検討する必要がある。UIの改善とパフォーマンス最適化が重要。"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={8}
              className="resize-none"
            />
            <p className="text-xs text-neutral-500">
              ヒント: Ctrl+Enter で送信
            </p>
          </div>
          <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <Sparkles className="size-5 text-blue-600 flex-shrink-0" />
            <p className="text-sm text-blue-900">
              メモ作成後、ローカルAIがタスクを自動生成します
            </p>
          </div>
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => {
              setOpen(false);
              setTitle("");
              setContent("");
            }}
          >
            キャンセル
          </Button>
          <Button onClick={handleCreate} disabled={!content.trim()}>
            <Sparkles className="size-4 mr-2" />
            メモを作成してAI処理を開始
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}