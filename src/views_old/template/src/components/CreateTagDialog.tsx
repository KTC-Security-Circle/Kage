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
import { Tag as TagType } from "../App";
import { Plus, Tag } from "lucide-react";

type CreateTagDialogProps = {
  onCreateTag: (tag: TagType) => void;
  trigger?: React.ReactNode;
};

const PRESET_COLORS = [
  "#3b82f6", // blue
  "#10b981", // green
  "#f59e0b", // amber
  "#8b5cf6", // violet
  "#ef4444", // red
  "#06b6d4", // cyan
  "#ec4899", // pink
  "#84cc16", // lime
  "#64748b", // slate
  "#a855f7", // purple
  "#14b8a6", // teal
  "#f97316", // orange
];

export function CreateTagDialog({
  onCreateTag,
  trigger,
}: CreateTagDialogProps) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [color, setColor] = useState(PRESET_COLORS[0]);

  const handleCreate = () => {
    if (!name.trim()) return;

    const newTag: TagType = {
      id: `tag-${Date.now()}`,
      name: name.trim().toLowerCase().replace(/\s+/g, "-"),
      description: description.trim() || undefined,
      color: color,
    };

    onCreateTag(newTag);
    resetForm();
    setOpen(false);
  };

  const resetForm = () => {
    setName("");
    setDescription("");
    setColor(PRESET_COLORS[0]);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Plus className="size-4 mr-2" />
            新しいタグ
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Tag className="size-5" />
            新しいタグを作成
          </DialogTitle>
          <DialogDescription>
            タグの詳細を入力してください。
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="tag-name">
              タグ名 <span className="text-red-500">*</span>
            </Label>
            <Input
              id="tag-name"
              placeholder="例: development, marketing, urgent"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <p className="text-xs text-neutral-500">
              スペースはハイフン(-)に自動変換されます
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="tag-description">説明（任意）</Label>
            <Textarea
              id="tag-description"
              placeholder="タグの用途や意味を入力..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="resize-none"
            />
          </div>

          <div className="space-y-2">
            <Label>カラー</Label>
            <div className="grid grid-cols-6 gap-2">
              {PRESET_COLORS.map((presetColor) => (
                <button
                  key={presetColor}
                  type="button"
                  className={`h-10 w-full rounded-md border-2 transition-all ${
                    color === presetColor
                      ? "border-neutral-900 scale-110"
                      : "border-transparent hover:scale-105"
                  }`}
                  style={{ backgroundColor: presetColor }}
                  onClick={() => setColor(presetColor)}
                  aria-label={`色を ${presetColor} に設定`}
                />
              ))}
            </div>
            <div className="flex items-center gap-2 mt-2">
              <Input
                type="color"
                value={color}
                onChange={(e) => setColor(e.target.value)}
                className="w-20 h-10 cursor-pointer"
              />
              <Input
                type="text"
                value={color}
                onChange={(e) => setColor(e.target.value)}
                placeholder="#3b82f6"
                className="flex-1"
              />
            </div>
          </div>

          <div className="p-3 bg-neutral-50 rounded-lg border">
            <p className="text-sm text-neutral-600 mb-2">プレビュー:</p>
            <div
              className="inline-flex items-center px-3 py-1 rounded-full text-sm"
              style={{
                backgroundColor: color + "20",
                borderColor: color,
                color: color,
                borderWidth: 1,
              }}
            >
              <Tag className="size-3 mr-1" />
              {name.trim().toLowerCase().replace(/\s+/g, "-") || "タグ名"}
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => {
              setOpen(false);
              resetForm();
            }}
          >
            キャンセル
          </Button>
          <Button onClick={handleCreate} disabled={!name.trim()}>
            <Plus className="size-4 mr-2" />
            タグを作成
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
