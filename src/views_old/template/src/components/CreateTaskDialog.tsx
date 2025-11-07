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
import { Task, Project } from "../App";
import { Plus, CheckSquare } from "lucide-react";

type CreateTaskDialogProps = {
  onCreateTask: (task: Task) => void;
  projects: Project[];
  trigger?: React.ReactNode;
};

export function CreateTaskDialog({
  onCreateTask,
  projects,
  trigger,
}: CreateTaskDialogProps) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [projectId, setProjectId] = useState<string | undefined>(undefined);
  const [dueDate, setDueDate] = useState("");

  const handleCreate = () => {
    if (!title.trim()) return;

    const newTask: Task = {
      id: `task-${Date.now()}`,
      title: title.trim(),
      description: description.trim() || undefined,
      status: "todo",
      projectId: projectId || undefined,
      tags: [],
      dueDate: dueDate ? new Date(dueDate) : undefined,
      isRecurring: false,
      createdAt: new Date(),
    };

    onCreateTask(newTask);
    resetForm();
    setOpen(false);
  };

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setProjectId(undefined);
    setDueDate("");
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Plus className="size-4 mr-2" />
            新しいタスク
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CheckSquare className="size-5" />
            新しいタスクを作成
          </DialogTitle>
          <DialogDescription>
            タスクの詳細を入力してください。
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="task-title">
              タイトル <span className="text-red-500">*</span>
            </Label>
            <Input
              id="task-title"
              placeholder="タスクのタイトルを入力..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="task-description">説明（任意）</Label>
            <Textarea
              id="task-description"
              placeholder="タスクの詳細を入力..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              className="resize-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="task-project">プロジェクト（任意）</Label>
              <Select value={projectId} onValueChange={setProjectId}>
                <SelectTrigger id="task-project">
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
              <Label htmlFor="task-due-date">期限（任意）</Label>
              <Input
                id="task-due-date"
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
            タスクを作成
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
