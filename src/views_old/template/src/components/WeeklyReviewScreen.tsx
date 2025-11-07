import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Separator } from "./ui/separator";
import { Checkbox } from "./ui/checkbox";
import { AppData } from "../App";
import {
  CalendarCheck,
  CheckCircle,
  Inbox,
  Clock,
  CalendarDays,
  TrendingUp,
  AlertCircle,
} from "lucide-react";

type WeeklyReviewScreenProps = {
  data: AppData;
  navigateTo: (screen: string, itemId?: string) => void;
};

export function WeeklyReviewScreen({ data, navigateTo }: WeeklyReviewScreenProps) {
  const reviewChecklist = [
    { id: "collect", label: "すべてのインボックスを空にする", completed: false },
    { id: "process", label: "各タスクを整理し、適切なリストに移動する", completed: false },
    { id: "review-calendar", label: "先週と来週のカレンダーを確認", completed: false },
    { id: "review-waiting", label: "待機中リストを確認", completed: false },
    { id: "review-projects", label: "進行中のプロジェクトを確認", completed: false },
    { id: "review-someday", label: "いつか/多分リストを見直す", completed: false },
    { id: "next-actions", label: "次のアクションを決定", completed: false },
  ];

  const inboxTasks = data.tasks.filter((t) => t.status === "inbox");
  const nextTasks = data.tasks.filter((t) => t.status === "next");
  const waitingTasks = data.tasks.filter((t) => t.status === "waiting");
  const somedayTasks = data.tasks.filter((t) => t.status === "someday");
  const completedTasks = data.tasks.filter((t) => t.status === "completed");
  const activeProjects = data.projects.filter((p) => p.status === "active");

  const oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
  const thisWeekCompleted = completedTasks.filter(
    (t) => t.createdAt >= oneWeekAgo
  ).length;

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1>週次レビュー</h1>
        <p className="text-neutral-600 mt-2">
          GTDの週次レビュー - システム全体を見直して整理する時間
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 統計概要 */}
        <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">今週完了</CardTitle>
                <TrendingUp className="size-4 text-gray-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl">{thisWeekCompleted}</div>
              <p className="text-neutral-600 text-xs mt-1">タスク</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">インボックス</CardTitle>
                <Inbox className="size-4 text-gray-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl">{inboxTasks.length}</div>
              <p className="text-neutral-600 text-xs mt-1">未整理</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">待機中</CardTitle>
                <Clock className="size-4 text-gray-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl">{waitingTasks.length}</div>
              <p className="text-neutral-600 text-xs mt-1">確認が必要</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">進行中PJ</CardTitle>
                <CalendarCheck className="size-4 text-gray-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl">{activeProjects.length}</div>
              <p className="text-neutral-600 text-xs mt-1">プロジェクト</p>
            </CardContent>
          </Card>
        </div>

        {/* レビューチェックリスト */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <CalendarCheck className="size-5 text-blue-600" />
                <CardTitle>週次レビューチェックリスト</CardTitle>
              </div>
              <CardDescription>
                GTDの週次レビュープロセスに従って、システムを整理しましょう
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {reviewChecklist.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center gap-3 p-3 rounded-lg hover:bg-neutral-50 transition-colors"
                  >
                    <Checkbox id={item.id} />
                    <label
                      htmlFor={item.id}
                      className="flex-1 cursor-pointer select-none"
                    >
                      {item.label}
                    </label>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 要注意事項 */}
          {inboxTasks.length > 0 && (
            <Card className="border-orange-200 bg-orange-50">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <AlertCircle className="size-5 text-orange-600" />
                  <CardTitle className="text-base">要整理</CardTitle>
                </div>
                <CardDescription>
                  インボックスに未整理のタスクがあります
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  variant="outline"
                  onClick={() => navigateTo("tasks")}
                  className="w-full"
                >
                  <Inbox className="size-4 mr-2" />
                  {inboxTasks.length} 件のタスクを整理する
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* 各リストの確認 */}
        <div className="space-y-4">
          {/* 次のアクション */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2">
                  <CheckCircle className="size-4 text-gray-600" />
                  次のアクション
                </CardTitle>
                <Badge>{nextTasks.length}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              {nextTasks.length === 0 ? (
                <p className="text-sm text-neutral-500 text-center py-2">
                  タスクなし
                </p>
              ) : (
                <div className="space-y-2">
                  {nextTasks.slice(0, 3).map((task) => (
                    <div
                      key={task.id}
                      className="p-2 text-sm border rounded cursor-pointer hover:border-neutral-300"
                      onClick={() => navigateTo("tasks", task.id)}
                    >
                      <div className="flex items-center gap-2">
                        <span className="line-clamp-1">{task.title}</span>
                        {task.priority === "high" && (
                          <Badge variant="destructive" className="text-xs">
                            高
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                  {nextTasks.length > 3 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-full"
                      onClick={() => navigateTo("tasks")}
                    >
                      さらに {nextTasks.length - 3} 件を表示
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* 待機中 */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2">
                  <Clock className="size-4 text-gray-600" />
                  待機中
                </CardTitle>
                <Badge>{waitingTasks.length}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              {waitingTasks.length === 0 ? (
                <p className="text-sm text-neutral-500 text-center py-2">
                  タスクなし
                </p>
              ) : (
                <div className="space-y-2">
                  {waitingTasks.slice(0, 3).map((task) => (
                    <div
                      key={task.id}
                      className="p-2 text-sm border rounded cursor-pointer hover:border-neutral-300"
                      onClick={() => navigateTo("tasks", task.id)}
                    >
                      <span className="line-clamp-1">{task.title}</span>
                    </div>
                  ))}
                  {waitingTasks.length > 3 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-full"
                      onClick={() => navigateTo("tasks")}
                    >
                      さらに {waitingTasks.length - 3} 件を表示
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* いつか/多分 */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2">
                  <CalendarDays className="size-4 text-gray-600" />
                  いつか/多分
                </CardTitle>
                <Badge>{somedayTasks.length}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              {somedayTasks.length === 0 ? (
                <p className="text-sm text-neutral-500 text-center py-2">
                  タスクなし
                </p>
              ) : (
                <div className="space-y-2">
                  {somedayTasks.slice(0, 3).map((task) => (
                    <div
                      key={task.id}
                      className="p-2 text-sm border rounded cursor-pointer hover:border-neutral-300"
                      onClick={() => navigateTo("tasks", task.id)}
                    >
                      <span className="line-clamp-1">{task.title}</span>
                    </div>
                  ))}
                  {somedayTasks.length > 3 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-full"
                      onClick={() => navigateTo("tasks")}
                    >
                      さらに {somedayTasks.length - 3} 件を表示
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      <Separator />

      {/* アクション */}
      <div className="flex justify-center gap-4">
        <Button variant="outline" onClick={() => navigateTo("tasks")}>
          タスクを整理する
        </Button>
        <Button variant="outline" onClick={() => navigateTo("projects")}>
          プロジェクトを確認
        </Button>
        <Button onClick={() => navigateTo("home")}>
          レビュー完了
        </Button>
      </div>
    </div>
  );
}
