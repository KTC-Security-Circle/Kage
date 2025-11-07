import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Project } from "../App";
import { Save, FolderOpen } from "lucide-react";

type EditProjectDialogProps = {
  project: Project;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  onProjectUpdate: (project: Project) => void;
  trigger?: React.ReactNode;
};

export function EditProjectDialog({
  project,
  open: controlledOpen,
  onOpenChange: controlledOnOpenChange,
  onProjectUpdate,
  trigger,
}: EditProjectDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false);
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const setOpen = controlledOnOpenChange || setInternalOpen;

  const [title, setTitle] = useState(project.title);
  const [description, setDescription] = useState(project.description || "");
  const [status, setStatus] = useState<Project["status"]>(project.status);
  const [dueDate, setDueDate] = useState(
    project.dueDate ? new Date(project.dueDate).toISOString().split("T")[0] : ""
  );

  useEffect(() => {
    if (open) {
      setTitle(project.title);
      setDescription(project.description || "");
      setStatus(project.status);
      setDueDate(project.dueDate ? new Date(project.dueDate).toISOString().split("T")[0] : "");
    }
  }, [open, project]);

  const handleUpdate = () => {
    if (!title.trim()) return;

    const updatedProject: Project = {
      ...project,
      title: title.trim(),
      description: description.trim() || undefined,
      status,
      dueDate: dueDate ? new Date(dueDate) : undefined,
      updatedAt: new Date(),
    };

    onProjectUpdate(updatedProject);
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || <Button>編集</Button>}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FolderOpen className="size-5" />
            プロジェクトを編集
          </DialogTitle>
          <DialogDescription>
            プロジェクトの詳細を編集してください。
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="edit-project-title">
              タイトル <span className="text-red-500">*</span>
            </Label>
            <Input
              id="edit-project-title"
              placeholder="プロジェクトのタイトルを入力..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-project-description">説明（任意）</Label>
            <Textarea
              id="edit-project-description"
              placeholder="プロジェクトの詳細を入力..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              className="resize-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="edit-project-status">ステータス</Label>
              <Select value={status} onValueChange={(value) => setStatus(value as Project["status"])}>
                <SelectTrigger id="edit-project-status">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">進行中</SelectItem>
                  <SelectItem value="on_hold">保留</SelectItem>
                  <SelectItem value="completed">完了</SelectItem>
                  <SelectItem value="cancelled">キャンセル</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-project-due-date">期限（任意）</Label>
              <Input
                id="edit-project-due-date"
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
            onClick={() => setOpen(false)}
          >
            キャンセル
          </Button>
          <Button onClick={handleUpdate} disabled={!title.trim()}>
            <Save className="size-4 mr-2" />
            更新
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}