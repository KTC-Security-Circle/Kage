import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { AppData } from "../App";
import { ArrowRight, Sparkles, CheckSquare, FolderOpen, Clock, Plus, TrendingUp, Coffee, Zap, Target } from "lucide-react";

type HomeScreenProps = {
  data: AppData;
  navigateTo: (screen: string, itemId?: string) => void;
};

// レビューメッセージを生成する関数
function generateDailyReview(data: AppData) {
  const todaysTasks = data.tasks.filter((t) => t.status === "todays");
  const completedTasks = data.tasks.filter((t) => t.status === "completed");
  const todoTasks = data.tasks.filter((t) => t.status === "todo");
  const inboxMemos = data.memos.filter((m) => m.status === "inbox");
  const progressTasks = data.tasks.filter((t) => t.status === "progress");
  const overdueTasks = data.tasks.filter((t) => t.status === "overdue");
  
  // 今日のタスク完了率
  const todaysCompletionRate = todaysTasks.length > 0 
    ? Math.round((completedTasks.filter(t => todaysTasks.some(tt => tt.id === t.id)).length / todaysTasks.length) * 100)
    : 0;

  // 状況に応じたメッセージとアイコンを選択
  if (overdueTasks.length > 0) {
    return {
      icon: Target,
      color: "text-slate-900",
      bgColor: "bg-amber-50",
      borderColor: "border-amber-400",
      message: `${overdueTasks.length}件の期限超過タスクがあります。優先的に対処しましょう。`,
      action: "期限超過のタスクを確認"
    };
  }
  
  if (todaysTasks.length === 0 && todoTasks.length > 0) {
    return {
      icon: Coffee,
      color: "text-slate-900",
      bgColor: "bg-slate-50",
      borderColor: "border-slate-200",
      message: `今日のタスクがまだ設定されていません。${todoTasks.length}件のTODOから選んで始めましょう！`,
      action: "タスクを設定する"
    };
  }

  if (todaysTasks.length > 0 && progressTasks.length === 0) {
    return {
      icon: Zap,
      color: "text-slate-900",
      bgColor: "bg-slate-50",
      borderColor: "border-slate-200",
      message: `${todaysTasks.length}件のタスクが待っています。さあ、最初の一歩を踏み出しましょう！`,
      action: "タスクを開始する"
    };
  }

  if (progressTasks.length > 0) {
    return {
      icon: TrendingUp,
      color: "text-slate-900",
      bgColor: "bg-white",
      borderColor: "border-slate-200",
      message: `${progressTasks.length}件のタスクが進行中です。良いペースです、その調子で続けましょう！`,
      action: "進行中のタスクを見る"
    };
  }

  if (inboxMemos.length > 0) {
    return {
      icon: Sparkles,
      color: "text-slate-900",
      bgColor: "bg-slate-50",
      borderColor: "border-slate-200",
      message: `${inboxMemos.length}件のInboxメモがあります。AIにタスクを生成させて整理しましょう。`,
      action: "メモを整理する"
    };
  }

  if (completedTasks.length > 0 && todaysTasks.length === 0) {
    return {
      icon: CheckSquare,
      color: "text-slate-900",
      bgColor: "bg-white",
      borderColor: "border-slate-200",
      message: `素晴らしい！全てのタスクが完了しています。新しいメモを書いて次の目標を設定しましょう。`,
      action: "新しいメモを作成"
    };
  }

  return {
    icon: Coffee,
    color: "text-slate-900",
    bgColor: "bg-white",
    borderColor: "border-slate-200",
    message: "今日も良い一日にしましょう。まずはメモを書いて、やるべきことを整理しませんか？",
    action: "メモを作成する"
  };
}

export function HomeScreen({ data, navigateTo }: HomeScreenProps) {
  const inboxMemos = data.memos.filter((m) => m.status === "inbox");
  const todaysTasks = data.tasks.filter((t) => t.status === "todays");
  const todoTasks = data.tasks.filter((t) => t.status === "todo");
  const activeProjects = data.projects.filter((p) => p.status === "active");

  const dailyReview = generateDailyReview(data);
  const ReviewIcon = dailyReview.icon;

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>ホーム</h1>
          <p className="text-neutral-600 mt-2">今日のタスクとプロジェクトの概要</p>
        </div>
        <Button onClick={() => navigateTo("create-memo")}>
          <Plus className="size-4 mr-2" />
          新しいメモ
        </Button>
      </div>

      {/* デイリーレビュー */}
      <Card className={`${dailyReview.borderColor} ${dailyReview.bgColor}`}>
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-full bg-white shadow-sm ${dailyReview.color}`}>
              <ReviewIcon className="size-6" />
            </div>
            <div className="flex-1">
              <p className="text-lg">{dailyReview.message}</p>
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-3 bg-white"
                onClick={() => {
                  if (dailyReview.action.includes("期限超過")) {
                    navigateTo("tasks");
                  } else if (dailyReview.action.includes("メモ")) {
                    navigateTo("create-memo");
                  } else {
                    navigateTo("tasks");
                  }
                }}
              >
                {dailyReview.action}
                <ArrowRight className="size-4 ml-1" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Inboxメモ */}
      {inboxMemos.length > 0 && (
        <Card className="bg-slate-50 border-slate-300">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="size-5 text-slate-900" />
                <CardTitle>Inboxメモ</CardTitle>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigateTo("memos")}
              >
                すべて見る
                <ArrowRight className="size-4 ml-1" />
              </Button>
            </div>
            <CardDescription>
              整理が必要なメモがあります。AIにタスクを生成させましょう。
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {inboxMemos.slice(0, 3).map((memo) => (
                <div
                  key={memo.id}
                  className="p-3 bg-white rounded-lg border border-slate-200 cursor-pointer hover:border-slate-400 transition-colors"
                  onClick={() => navigateTo("memos", memo.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span>{memo.title}</span>
                        {memo.aiSuggestionStatus === "available" && (
                          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-300">
                            AI提案あり
                          </Badge>
                        )}
                        {memo.aiSuggestionStatus === "pending" && (
                          <Badge variant="outline" className="bg-slate-100 text-slate-700 border-slate-300">
                            AI処理中
                          </Badge>
                        )}
                        {memo.aiSuggestionStatus === "not_requested" && (
                          <Badge variant="outline">AI未実行</Badge>
                        )}
                      </div>
                      <p className="text-neutral-600 text-sm mt-1 line-clamp-2">
                        {memo.content}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 統計カード */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card
          className="cursor-pointer hover:shadow-md transition-shadow bg-white"
          onClick={() => navigateTo("tasks")}
        >
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">次のアクション</CardTitle>
              <CheckSquare className="size-5 text-slate-900" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl">{todaysTasks.length}</div>
            <p className="text-neutral-600 text-sm mt-1">件のタスク</p>
          </CardContent>
        </Card>

        <Card
          className="cursor-pointer hover:shadow-md transition-shadow bg-white"
          onClick={() => navigateTo("tasks")}
        >
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">インボックス</CardTitle>
              <Clock className="size-5 text-slate-900" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl">{todoTasks.length}</div>
            <p className="text-neutral-600 text-sm mt-1">未処理のタスク</p>
          </CardContent>
        </Card>

        <Card
          className="cursor-pointer hover:shadow-md transition-shadow bg-white"
          onClick={() => navigateTo("projects")}
        >
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">進行中プロジェクト</CardTitle>
              <FolderOpen className="size-5 text-slate-900" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl">{activeProjects.length}</div>
            <p className="text-neutral-600 text-sm mt-1">件のプロジェクト</p>
          </CardContent>
        </Card>
      </div>

      {/* 次のアクション */}
      {/* <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>次のアクション</CardTitle>
            <Button variant="ghost" size="sm" onClick={() => navigateTo("tasks")}>
              すべて見る
              <ArrowRight className="size-4 ml-1" />
            </Button>
          </div>
          <CardDescription>今日やるべきタスク</CardDescription>
        </CardHeader>
        <CardContent>
          {todaysTasks.length === 0 ? (
            <p className="text-neutral-500 text-center py-4">
              タスクはありません。素晴らしい！
            </p>
          ) : (
            <div className="space-y-2">
              {todaysTasks.slice(0, 5).map((task) => (
                <div
                  key={task.id}
                  className="p-3 rounded-lg border hover:border-neutral-300 cursor-pointer transition-colors"
                  onClick={() => navigateTo("tasks", task.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span>{task.title}</span>
                      </div>
                      <p className="text-neutral-600 text-sm mt-1">{task.description}</p>
                      <div className="flex items-center gap-2 mt-2">
                        {task.tags.map((tagName) => {
                          const tag = data.tags.find((t) => t.name === tagName);
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
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card> */}

      {/* アクティブプロジェクト */}
      {/* <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>進行中のプロジェクト</CardTitle>
            <Button variant="ghost" size="sm" onClick={() => navigateTo("projects")}>
              すべて見る
              <ArrowRight className="size-4 ml-1" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {activeProjects.length === 0 ? (
            <p className="text-neutral-500 text-center py-4">
              進行中のプロジェクトはありません
            </p>
          ) : (
            <div className="space-y-3">
              {activeProjects.map((project) => (
                <div
                  key={project.id}
                  className="p-4 rounded-lg border hover:border-neutral-300 cursor-pointer transition-colors"
                  onClick={() => navigateTo("projects", project.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div>{project.title}</div>
                      <p className="text-neutral-600 text-sm mt-1">{project.description}</p>
                      <div className="flex items-center gap-4 mt-3">
                        <div className="text-sm text-neutral-600">
                          {data.tasks.filter((t) => t.projectId === project.id).length} タスク
                        </div>
                      </div>
                    </div>
                    <Badge
                      variant={
                        project.status === "active"
                          ? "default"
                          : project.status === "completed"
                            ? "secondary"
                            : "outline"
                      }
                    >
                      {project.status === "active"
                        ? "進行中"
                        : project.status === "completed"
                          ? "完了"
                          : project.status === "on_hold"
                            ? "保留中"
                            : "キャンセル"}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card> */}
    </div>
  );
}