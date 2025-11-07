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
import { Task, Project } from "../App";
import { Save, CheckSquare } from "lucide-react";

type EditTaskDialogProps = {
  task: Task;
  projects: Project[];
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  onTaskUpdate: (task: Task) => void;
  trigger?: React.ReactNode;
};

export function EditTaskDialog({
  task,
  projects,
  open: controlledOpen,
  onOpenChange: controlledOnOpenChange,
  onTaskUpdate,
  trigger,
}: EditTaskDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false);
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const setOpen = controlledOnOpenChange || setInternalOpen;

  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || "");
  const [status, setStatus] = useState<Task["status"]>(task.status);
  const [projectId, setProjectId] = useState<string | undefined>(task.projectId);
  const [dueDate, setDueDate] = useState(
    task.dueDate ? new Date(task.dueDate).toISOString().split("T")[0] : ""
  );

  useEffect(() => {
    if (open) {
      setTitle(task.title);
      setDescription(task.description || "");
      setStatus(task.status);
      setProjectId(task.projectId);
      setDueDate(task.dueDate ? new Date(task.dueDate).toISOString().split("T")[0] : "");
    }
  }, [open, task]);

  const handleUpdate = () => {
    if (!title.trim()) return;

    const updatedTask: Task = {
      ...task,
      title: title.trim(),
      description: description.trim() || "",
      status,
      projectId: projectId === "none" ? undefined : projectId,
      dueDate: dueDate ? new Date(dueDate) : undefined,
    };

    onTaskUpdate(updatedTask);
    setOpen(false);
  };

  const getStatusLabel = (status: Task["status"]) => {
    const labels: Record<Task["status"], string> = {
      todo: "TODO",
      todays: "今日のタスク",
      progress: "進行中",
      waiting: "待機中",
      completed: "完了",
      canceled: "キャンセル",
      overdue: "期限切れ",
    };
    return labels[status];
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || <Button>編集</Button>}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CheckSquare className="size-5" />
            タスクを編集
          </DialogTitle>
          <DialogDescription>
            タスクの詳細を編集してください。
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="edit-task-title">
              タイトル <span className="text-red-500">*</span>
            </Label>
            <Input
              id="edit-task-title"
              placeholder="タスクのタイトルを入力..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-task-description">説明（任意）</Label>
            <Textarea
              id="edit-task-description"
              placeholder="タスクの詳細を入力..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              className="resize-none"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-task-status">ステータス</Label>
            <Select value={status} onValueChange={(value) => setStatus(value as Task["status"])}>
              <SelectTrigger id="edit-task-status">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todo">{getStatusLabel("todo")}</SelectItem>
                <SelectItem value="todays">{getStatusLabel("todays")}</SelectItem>
                <SelectItem value="progress">{getStatusLabel("progress")}</SelectItem>
                <SelectItem value="waiting">{getStatusLabel("waiting")}</SelectItem>
                <SelectItem value="completed">{getStatusLabel("completed")}</SelectItem>
                <SelectItem value="canceled">{getStatusLabel("canceled")}</SelectItem>
                <SelectItem value="overdue">{getStatusLabel("overdue")}</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="edit-task-project">プロジェクト（任意）</Label>
              <Select value={projectId || "none"} onValueChange={setProjectId}>
                <SelectTrigger id="edit-task-project">
                  <SelectValue placeholder="プロジェクトを選択" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">なし</SelectItem>
                  {projects
                    .filter((p) => p.status === "active")
                    .map((project) => (
                      <SelectItem key={project.id} value={project.id}>
                        {project.title}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-task-due-date">期限（任意）</Label>
              <Input
                id="edit-task-due-date"
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