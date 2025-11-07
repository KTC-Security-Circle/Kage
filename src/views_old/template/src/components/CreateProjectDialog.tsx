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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Project } from "../App";
import { Plus, FolderOpen } from "lucide-react";

type CreateProjectDialogProps = {
  onCreateProject: (project: Project) => void;
  trigger?: React.ReactNode;
};

export function CreateProjectDialog({
  onCreateProject,
  trigger,
}: CreateProjectDialogProps) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<Project["status"]>("active");
  const [dueDate, setDueDate] = useState("");

  const handleCreate = () => {
    if (!title.trim()) return;

    const newProject: Project = {
      id: `project-${Date.now()}`,
      title: title.trim(),
      description: description.trim() || undefined,
      status: status,
      dueDate: dueDate ? new Date(dueDate) : undefined,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    onCreateProject(newProject);
    resetForm();
    setOpen(false);
  };

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setStatus("active");
    setDueDate("");
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Plus className="size-4 mr-2" />
            新しいプロジェクト
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FolderOpen className="size-5" />
            新しいプロジェクトを作成
          </DialogTitle>
          <DialogDescription>
            プロジェクトの詳細を入力してください。
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="project-title">
              タイトル <span className="text-red-500">*</span>
            </Label>
            <Input
              id="project-title"
              placeholder="プロジェクトのタイトルを入力..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="project-description">説明（任意）</Label>
            <Textarea
              id="project-description"
              placeholder="プロジェクトの詳細を入力..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              className="resize-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="project-status">ステータス</Label>
              <Select value={status} onValueChange={(value) => setStatus(value as Project["status"])}>
                <SelectTrigger id="project-status">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">進行中</SelectItem>
                  <SelectItem value="on_hold">保留</SelectItem>
                  <SelectItem value="completed">完了</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="project-due-date">期限（任意）</Label>
              <Input
                id="project-due-date"
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
              />
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
          <Button onClick={handleCreate} disabled={!title.trim()}>
            <Plus className="size-4 mr-2" />
            プロジェクトを作成
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
