import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Task, Project, Memo, Tag } from "../App";
import { 
  ListTodo, 
  CalendarClock, 
  PlayCircle, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  ExternalLink,
  Edit2,
  Search
} from "lucide-react";
import { CreateTaskDialog } from "./CreateTaskDialog";
import { EditTaskDialog } from "./EditTaskDialog";

type TasksScreenProps = {
  tasks: Task[];
  projects: Project[];
  memos: Memo[];
  tags: Tag[];
  navigateTo: (screen: string, itemId?: string) => void;
  selectedTaskId?: string | null;
  onTaskUpdate: (task: Task) => void;
  onTaskCreate: (task: Task) => void;
};

export function TasksScreen({
  tasks,
  projects,
  memos,
  tags,
  navigateTo,
  selectedTaskId,
  onTaskUpdate,
  onTaskCreate,
}: TasksScreenProps) {
  const [selectedTask, setSelectedTask] = useState<Task | null>(
    selectedTaskId ? tasks.find((t) => t.id === selectedTaskId) || null : null
  );
  const [searchQuery, setSearchQuery] = useState("");

  const filterTasks = (tasksList: Task[]) => {
    if (!searchQuery) return tasksList;
    const query = searchQuery.toLowerCase();
    return tasksList.filter(
      (task) =>
        task.title.toLowerCase().includes(query) ||
        task.description?.toLowerCase().includes(query) ||
        task.tags.some((tag) => tag.toLowerCase().includes(query))
    );
  };

  const getTasksByStatus = (status: Task["status"]) => {
    return filterTasks(tasks.filter((t) => t.status === status));
  };

  const handleStatusChange = (task: Task, newStatus: Task["status"]) => {
    onTaskUpdate({ ...task, status: newStatus });
    if (selectedTask?.id === task.id) {
      setSelectedTask({ ...task, status: newStatus });
    }
  };

  const renderTaskCard = (task: Task) => {
    const project = task.projectId
      ? projects.find((p) => p.id === task.projectId)
      : null;
    const memo = task.memoId ? memos.find((m) => m.id === task.memoId) : null;

    return (
      <div
        key={task.id}
        className={`p-4 border rounded-lg cursor-pointer transition-all ${
          selectedTask?.id === task.id
            ? "border-blue-500 shadow-md bg-blue-50"
            : "hover:border-neutral-300 bg-white"
        }`}
        onClick={() => setSelectedTask(task)}
      >
        <div className="space-y-2">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span>{task.title}</span>
                {task.isRecurring && (
                  <Badge variant="outline" className="text-xs">
                    繰り返し
                  </Badge>
                )}
              </div>
              <p className="text-neutral-600 text-sm mt-1">{task.description}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            {project && (
              <Badge
                variant="outline"
                className="text-xs cursor-pointer"
                onClick={(e) => {
                  e.stopPropagation();
                  navigateTo("projects", project.id);
                }}
              >
                {project.title}
              </Badge>
            )}
            {task.tags.map((tagName) => {
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
          {memo && (
            <div className="text-xs text-neutral-500 flex items-center gap-1">
              <ExternalLink className="size-3" />
              <span
                className="cursor-pointer hover:underline"
                onClick={(e) => {
                  e.stopPropagation();
                  navigateTo("memo-history", memo.id);
                }}
              >
                メモから生成
              </span>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col">
      {/* ヘッダー */}
      <div className="p-6 border-b bg-white">
        <div className="flex items-center justify-between">
          <div>
            <h1>タスク</h1>
            <p className="text-neutral-600 mt-1">GTDベースのタスク管理 ({tasks.length}件)</p>
          </div>
          <div className="flex items-center gap-3">
            {/* 検索バー */}
            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-neutral-400" />
              <Input
                placeholder="タスクを検索..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <CreateTaskDialog onCreateTask={onTaskCreate} projects={projects} />
          </div>
        </div>
      </div>

      {/* メインコンテンツ */}
      <div className="flex-1 overflow-hidden">
        <Tabs defaultValue="todays" className="h-full flex flex-col">
          {/* タブを横長に配置 */}
          <div className="px-6 pt-4 border-b bg-white">
            <TabsList className="grid w-full grid-cols-7">
              <TabsTrigger value="todo" className="flex items-center gap-1">
                <ListTodo className="size-4" />
                <span className="hidden sm:inline">TODO</span>
                <Badge variant="secondary" className="ml-1 text-xs">
                  {getTasksByStatus("todo").length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger value="todays" className="flex items-center gap-1">
                <CalendarClock className="size-4" />
                <span className="hidden sm:inline">今日</span>
                <Badge variant="secondary" className="ml-1 text-xs">
                  {getTasksByStatus("todays").length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger value="progress" className="flex items-center gap-1">
                <PlayCircle className="size-4" />
                <span className="hidden sm:inline">進行中</span>
                <Badge variant="secondary" className="ml-1 text-xs">
                  {getTasksByStatus("progress").length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger value="waiting" className="flex items-center gap-1">
                <Clock className="size-4" />
                <span className="hidden sm:inline">待機中</span>
                <Badge variant="secondary" className="ml-1 text-xs">
                  {getTasksByStatus("waiting").length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger value="completed" className="flex items-center gap-1">
                <CheckCircle className="size-4" />
                <span className="hidden sm:inline">完了</span>
                <Badge variant="secondary" className="ml-1 text-xs">
                  {getTasksByStatus("completed").length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger value="canceled" className="flex items-center gap-1">
                <XCircle className="size-4" />
                <span className="hidden sm:inline">キャンセル</span>
                <Badge variant="secondary" className="ml-1 text-xs">
                  {getTasksByStatus("canceled").length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger value="overdue" className="flex items-center gap-1">
                <AlertTriangle className="size-4" />
                <span className="hidden sm:inline">期限超過</span>
                <Badge variant="secondary" className="ml-1 text-xs">
                  {getTasksByStatus("overdue").length}
                </Badge>
              </TabsTrigger>
            </TabsList>
          </div>

          <div className="flex-1 overflow-hidden">
            <div className="h-full grid grid-cols-1 lg:grid-cols-5 gap-6 p-6">
              {/* 左側：スクリスト */}
              <div className="lg:col-span-2 overflow-y-auto space-y-4">
                <TabsContent value="todo" className="space-y-3">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base flex items-center gap-2">
                        <ListTodo className="size-5" />
                        TODO
                      </CardTitle>
                      <CardDescription>
                        これから取り組むべきタスク
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {getTasksByStatus("todo").length === 0 ? (
                        <p className="text-center text-neutral-500 py-4">
                          TODOタスクはありません
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {getTasksByStatus("todo").map((task) => renderTaskCard(task))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="todays" className="space-y-3">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base flex items-center gap-2">
                        <CalendarClock className="size-5 text-slate-900" />
                        今日のタスク
                      </CardTitle>
                      <CardDescription>
                        今日中に完了させるべきタスク
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {getTasksByStatus("todays").length === 0 ? (
                        <p className="text-center text-neutral-500 py-4">
                          今日のタスクはありません
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {getTasksByStatus("todays").map((task) => renderTaskCard(task))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="progress" className="space-y-3">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base flex items-center gap-2">
                        <PlayCircle className="size-5 text-slate-900" />
                        進行中
                      </CardTitle>
                      <CardDescription>
                        現在進行中のタスク
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {getTasksByStatus("progress").length === 0 ? (
                        <p className="text-center text-neutral-500 py-4">
                          進行中のタスクはありません
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {getTasksByStatus("progress").map((task) => renderTaskCard(task))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="waiting" className="space-y-3">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base flex items-center gap-2">
                        <Clock className="size-5 text-slate-900" />
                        待機中
                      </CardTitle>
                      <CardDescription>
                        他のタスクの完了を待っているタスク
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {getTasksByStatus("waiting").length === 0 ? (
                        <p className="text-center text-neutral-500 py-4">
                          待機中のタスクはありません
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {getTasksByStatus("waiting").map((task) => renderTaskCard(task))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="completed" className="space-y-3">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base flex items-center gap-2">
                        <CheckCircle className="size-5 text-slate-900" />
                        完了
                      </CardTitle>
                      <CardDescription>完了したタスク</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {getTasksByStatus("completed").length === 0 ? (
                        <p className="text-center text-neutral-500 py-4">
                          完了したタスクはありません
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {getTasksByStatus("completed").map((task) => renderTaskCard(task))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="canceled" className="space-y-3">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base flex items-center gap-2">
                        <XCircle className="size-5 text-slate-900" />
                        キャンセル
                      </CardTitle>
                      <CardDescription>キャンセルされたタスク</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {getTasksByStatus("canceled").length === 0 ? (
                        <p className="text-center text-neutral-500 py-4">
                          キャンセルされたタスクはありません
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {getTasksByStatus("canceled").map((task) => renderTaskCard(task))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="overdue" className="space-y-3">
                  <Card className="border-amber-400 bg-amber-50">
                    <CardHeader>
                      <CardTitle className="text-base flex items-center gap-2">
                        <AlertTriangle className="size-5 text-slate-900" />
                        期限超過
                      </CardTitle>
                      <CardDescription className="text-amber-900">
                        期限が過ぎたタスク - 早急な対応が必要です
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {getTasksByStatus("overdue").length === 0 ? (
                        <p className="text-center text-neutral-500 py-4">
                          期限超過のタスクはありませ
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {getTasksByStatus("overdue").map((task) => renderTaskCard(task))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>
              </div>

              {/* 右側：タスク詳細 */}
              <div className="lg:col-span-3 overflow-y-auto">
                {selectedTask ? (
                  <Card className="sticky top-6">
                    <CardHeader>
                      <CardTitle className="text-base">タスク詳細</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <div className="text-sm text-neutral-500 mb-1">タイトル</div>
                        <div>{selectedTask.title}</div>
                      </div>
                      <div>
                        <div className="text-sm text-neutral-500 mb-1">説明</div>
                        <p className="text-sm">{selectedTask.description}</p>
                      </div>
                      <div>
                        <div className="text-sm text-neutral-500 mb-2">ステータス</div>
                        <Select
                          value={selectedTask.status}
                          onValueChange={(value) =>
                            handleStatusChange(selectedTask, value as Task["status"])
                          }
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="todo">TODO</SelectItem>
                            <SelectItem value="todays">今日</SelectItem>
                            <SelectItem value="progress">進行中</SelectItem>
                            <SelectItem value="waiting">待機中</SelectItem>
                            <SelectItem value="completed">完了</SelectItem>
                            <SelectItem value="canceled">キャンセル</SelectItem>
                            <SelectItem value="overdue">期限超過</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      {selectedTask.isRecurring && (
                        <div>
                          <div className="text-sm text-neutral-500 mb-1">繰り返し設定</div>
                          <Badge variant="outline">繰り返しタスク</Badge>
                          {selectedTask.recurrenceRule && (
                            <p className="text-xs text-neutral-500 mt-1">
                              {selectedTask.recurrenceRule}
                            </p>
                          )}
                        </div>
                      )}
                      {selectedTask.projectId && (
                        <div>
                          <div className="text-sm text-neutral-500 mb-1">プロジェクト</div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => navigateTo("projects", selectedTask.projectId)}
                          >
                            <ExternalLink className="size-4 mr-1" />
                            {
                              projects.find((p) => p.id === selectedTask.projectId)
                                ?.title
                            }
                          </Button>
                        </div>
                      )}
                      {selectedTask.memoId && (
                        <div>
                          <div className="text-sm text-neutral-500 mb-1">関連メモ</div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => navigateTo("memo-history", selectedTask.memoId)}
                          >
                            <ExternalLink className="size-4 mr-1" />
                            {memos.find((m) => m.id === selectedTask.memoId)?.title}
                          </Button>
                        </div>
                      )}
                      <div>
                        <div className="text-sm text-neutral-500 mb-2">タグ</div>
                        <div className="flex flex-wrap gap-1">
                          {selectedTask.tags.map((tagName) => {
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
                      </div>
                      <div>
                        <div className="text-sm text-neutral-500 mb-1">作成日</div>
                        <div className="text-sm">
                          {selectedTask.createdAt.toLocaleDateString('ja-JP')}
                        </div>
                      </div>
                      <div>
                        <EditTaskDialog
                          task={selectedTask}
                          projects={projects}
                          onTaskUpdate={(updatedTask) => {
                            onTaskUpdate(updatedTask);
                            setSelectedTask(updatedTask);
                          }}
                          trigger={
                            <Button variant="outline" className="w-full">
                              <Edit2 className="size-4 mr-2" />
                              編集
                            </Button>
                          }
                        />
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                  <Card>
                    <CardContent className="py-12">
                      <p className="text-center text-neutral-500">
                        タスクを選択して詳細を表示
                      </p>
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