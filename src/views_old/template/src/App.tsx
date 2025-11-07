import { useState } from "react";
import { SidebarProvider } from "./components/ui/sidebar";
import { AppSidebar } from "./components/AppSidebar";
import { HomeScreen } from "./components/HomeScreen";
import { MemosScreen } from "./components/MemosScreen";
import { TasksScreen } from "./components/TasksScreen";
import { ProjectsScreen } from "./components/ProjectsScreen";
import { TagsScreen } from "./components/TagsScreen";
import { TermsScreen } from "./components/TermsScreen";
import { WeeklyReviewScreen } from "./components/WeeklyReviewScreen";
import { SettingsScreen } from "./components/SettingsScreen";
import { CreateMemoScreen } from "./components/CreateMemoScreen";

export type Memo = {
  id: string;
  title: string;
  content: string;
  status: "inbox" | "active" | "idea" | "archive";
  aiSuggestionStatus:
    | "not_requested"
    | "pending"
    | "available"
    | "reviewed"
    | "failed";
  createdAt: Date;
  updatedAt: Date;
  processedAt?: Date;
  tags: string[];
};

export type Task = {
  id: string;
  title: string;
  description: string;
  status:
    | "todo"
    | "todays"
    | "progress"
    | "waiting"
    | "completed"
    | "canceled"
    | "overdue";
  projectId?: string;
  memoId?: string;
  tags: string[];
  dueDate?: Date;
  completedAt?: Date;
  isRecurring: boolean;
  recurrenceRule?: string;
  createdAt: Date;
};

export type Project = {
  id: string;
  title: string;
  description?: string;
  status: "active" | "on_hold" | "completed" | "cancelled";
  dueDate?: Date;
  createdAt: Date;
  updatedAt: Date;
};

export type Tag = {
  id: string;
  name: string;
  description?: string;
  color: string;
};

export type Term = {
  id: string;
  key: string;
  title: string;
  description?: string;
  status: "draft" | "approved" | "deprecated";
  sourceUrl?: string;
  synonyms: string[];
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
};

export type AppData = {
  memos: Memo[];
  tasks: Task[];
  projects: Project[];
  tags: Tag[];
  terms: Term[];
};

export default function App() {
  const [currentScreen, setCurrentScreen] =
    useState<string>("home");
  const [selectedItemId, setSelectedItemId] = useState<
    string | null
  >(null);

  // サンプルデータ
  const [appData, setAppData] = useState<AppData>({
    memos: [
      {
        id: "memo-1",
        title: "プロジェクトAのアイデア",
        content:
          "新しい機能の実装について検討する必要がある。UIの改善とパフォーマンス最適化が重要。ユーザーフィードバックを元に、ダッシュボードの再設計を行う。",
        status: "inbox",
        aiSuggestionStatus: "available",
        createdAt: new Date(2025, 9, 20),
        updatedAt: new Date(2025, 9, 20),
        tags: ["project-a", "development"],
      },
      {
        id: "memo-2",
        title: "週次ミーティングの議事録",
        content:
          "次週のタスクについて話し合った。優先順位を見直し、リソースを再配分する。プロジェクトBの進捗確認も必要。",
        status: "active",
        aiSuggestionStatus: "reviewed",
        createdAt: new Date(2025, 9, 18),
        updatedAt: new Date(2025, 9, 19),
        processedAt: new Date(2025, 9, 19),
        tags: ["meeting", "project-a"],
      },
      {
        id: "memo-3",
        title: "ランダムなアイデア",
        content:
          "ふ pigerついたこと。新しいマーケティング戦略について考える。",
        status: "idea",
        aiSuggestionStatus: "reviewed",
        createdAt: new Date(2025, 9, 15),
        updatedAt: new Date(2025, 9, 15),
        processedAt: new Date(2025, 9, 15),
        tags: ["marketing"],
      },
      {
        id: "memo-4",
        title: "顧客からのフィードバック",
        content:
          "モバイルアプリの読み込みが遅いという報告が複数あり。パフォーマンス改善が急務。",
        status: "inbox",
        aiSuggestionStatus: "not_requested",
        createdAt: new Date(2025, 9, 21),
        updatedAt: new Date(2025, 9, 21),
        tags: ["feedback", "mobile"],
      },
      {
        id: "memo-5",
        title: "セキュリティアップデート",
        content:
          "依存パッケージのセキュリティ脆弱性が報告された。早急に対応する必要がある。",
        status: "active",
        aiSuggestionStatus: "reviewed",
        createdAt: new Date(2025, 9, 17),
        updatedAt: new Date(2025, 9, 18),
        processedAt: new Date(2025, 9, 18),
        tags: ["security", "urgent"],
      },
      {
        id: "memo-6",
        title: "チームビルディングイベント",
        content:
          "来月のチームビルディングイベントのアイデア。ボーリング大会かエスケープルームを検討。",
        status: "idea",
        aiSuggestionStatus: "reviewed",
        createdAt: new Date(2025, 9, 12),
        updatedAt: new Date(2025, 9, 12),
        processedAt: new Date(2025, 9, 12),
        tags: ["team"],
      },
      {
        id: "memo-7",
        title: "Q4目標設定",
        content:
          "第4四半期の目標を設定する。売上15%増、新規顧客獲得50社、製品リリース2つ。",
        status: "active",
        aiSuggestionStatus: "reviewed",
        createdAt: new Date(2025, 9, 10),
        updatedAt: new Date(2025, 9, 11),
        processedAt: new Date(2025, 9, 11),
        tags: ["planning", "business"],
      },
      {
        id: "memo-8",
        title: "完了したプロジェクトの振り返り",
        content:
          "プロジェクトCが無事完了。成功要因と改善点をまとめた。",
        status: "archive",
        aiSuggestionStatus: "reviewed",
        createdAt: new Date(2025, 8, 25),
        updatedAt: new Date(2025, 9, 5),
        processedAt: new Date(2025, 8, 26),
        tags: ["project-c", "retrospective"],
      },
    ],
    tasks: [
      {
        id: "task-1",
        title: "UIコンポーネントの設計",
        description:
          "新しいダッシュボード用のコンポーネントを設計する",
        status: "todays",
        projectId: "project-1",
        memoId: "memo-2",
        tags: ["design", "project-a"],
        dueDate: new Date(2025, 9, 22),
        isRecurring: false,
        createdAt: new Date(2025, 9, 19),
      },
      {
        id: "task-2",
        title: "パフォーマンステストの実施",
        description: "負荷テストを行い、ボトルネックを特定する",
        status: "todo",
        projectId: "project-1",
        memoId: "memo-2",
        tags: ["testing", "project-a"],
        dueDate: new Date(2025, 9, 25),
        isRecurring: false,
        createdAt: new Date(2025, 9, 19),
      },
      {
        id: "task-3",
        title: "ドキュメントの更新",
        description: "APIドキュメントを最新の状態に更新する",
        status: "waiting",
        tags: ["documentation"],
        dueDate: new Date(2025, 9, 30),
        isRecurring: false,
        createdAt: new Date(2025, 9, 15),
      },
      {
        id: "task-4",
        title: "セキュリティパッチの適用",
        description:
          "依存パッケージのセキュリティアップデートを適用",
        status: "todays",
        memoId: "memo-5",
        tags: ["security", "urgent"],
        dueDate: new Date(2025, 9, 22),
        isRecurring: false,
        createdAt: new Date(2025, 9, 17),
      },
      {
        id: "task-5",
        title: "モバイルアプリの最適化",
        description: "読み込み速度を改善するための最適化作業",
        status: "progress",
        projectId: "project-2",
        tags: ["mobile", "performance"],
        dueDate: new Date(2025, 9, 28),
        isRecurring: false,
        createdAt: new Date(2025, 9, 20),
      },
      {
        id: "task-6",
        title: "週次レポートの作成",
        description: "進捗状況をまとめた週次レポートを作成",
        status: "completed",
        tags: ["reporting"],
        completedAt: new Date(2025, 9, 18),
        isRecurring: true,
        recurrenceRule: "FREQ=WEEKLY;BYDAY=FR",
        createdAt: new Date(2025, 9, 11),
      },
      {
        id: "task-7",
        title: "コードレビュー",
        description: "新機能のプルリクエストをレビューする",
        status: "todays",
        projectId: "project-1",
        tags: ["development", "review"],
        dueDate: new Date(2025, 9, 22),
        isRecurring: false,
        createdAt: new Date(2025, 9, 21),
      },
      {
        id: "task-8",
        title: "データベースのバックアップ",
        description: "本番環境のデータベースをバックアップ",
        status: "completed",
        tags: ["infrastructure"],
        completedAt: new Date(2025, 9, 20),
        isRecurring: true,
        recurrenceRule: "FREQ=DAILY",
        createdAt: new Date(2025, 9, 1),
      },
      {
        id: "task-9",
        title: "ユーザーインタビュー実施",
        description:
          "新機能に関するユーザーフィードバックを収集",
        status: "todo",
        projectId: "project-1",
        tags: ["research", "ux"],
        dueDate: new Date(2025, 9, 27),
        isRecurring: false,
        createdAt: new Date(2025, 9, 18),
      },
      {
        id: "task-10",
        title: "予算会議の準備",
        description: "次年度の予算案を準備",
        status: "waiting",
        tags: ["business", "planning"],
        dueDate: new Date(2025, 10, 5),
        isRecurring: false,
        createdAt: new Date(2025, 9, 10),
      },
      {
        id: "task-11",
        title: "マーケティング資料の作成",
        description: "新製品のマーケティング資料を作成",
        status: "canceled",
        projectId: "project-3",
        tags: ["marketing"],
        isRecurring: false,
        createdAt: new Date(2025, 9, 5),
      },
      {
        id: "task-12",
        title: "期限切れタスクの例",
        description: "これは期限が過ぎているタスクの例です",
        status: "overdue",
        tags: ["example"],
        dueDate: new Date(2025, 9, 15),
        isRecurring: false,
        createdAt: new Date(2025, 9, 10),
      },
    ],
    projects: [
      {
        id: "project-1",
        title: "プロジェクトA - 新機能開発",
        description:
          "ユーザー体験を向上させる新機能の開発プロジェクト。ダッシュボードの全面刷新とパフォーマンス改善を含む。",
        status: "active",
        dueDate: new Date(2025, 10, 30),
        createdAt: new Date(2025, 9, 10),
        updatedAt: new Date(2025, 9, 20),
      },
      {
        id: "project-2",
        title: "モバイルアプリ最適化",
        description:
          "モバイルアプリのパフォーマンス改善とUI/UX向上",
        status: "active",
        dueDate: new Date(2025, 10, 15),
        createdAt: new Date(2025, 9, 15),
        updatedAt: new Date(2025, 9, 20),
      },
      {
        id: "project-3",
        title: "マーケティングキャンペーン",
        description: "Q4の新規顧客獲得キャンペーン",
        status: "on_hold",
        dueDate: new Date(2025, 11, 31),
        createdAt: new Date(2025, 9, 1),
        updatedAt: new Date(2025, 9, 18),
      },
      {
        id: "project-4",
        title: "プロジェクトC - インフラ移行",
        description: "クラウドインフラの移行プロジェクト",
        status: "completed",
        dueDate: new Date(2025, 9, 1),
        createdAt: new Date(2025, 7, 1),
        updatedAt: new Date(2025, 9, 5),
      },
    ],
    tags: [
      {
        id: "tag-1",
        name: "project-a",
        description: "プロジェクトAに関連するアイテム",
        color: "#3b82f6",
      },
      {
        id: "tag-2",
        name: "development",
        description: "開発関連のタスク",
        color: "#10b981",
      },
      {
        id: "tag-3",
        name: "meeting",
        description: "ミーティング関連",
        color: "#f59e0b",
      },
      {
        id: "tag-4",
        name: "design",
        description: "デザイン関連のタスク",
        color: "#8b5cf6",
      },
      {
        id: "tag-5",
        name: "testing",
        description: "テスト関連のタスク",
        color: "#ef4444",
      },
      {
        id: "tag-6",
        name: "security",
        description: "セキュリティ関連",
        color: "#dc2626",
      },
      {
        id: "tag-7",
        name: "urgent",
        description: "緊急対応が必要",
        color: "#ff0000",
      },
      {
        id: "tag-8",
        name: "mobile",
        description: "モバイルアプリ関連",
        color: "#06b6d4",
      },
      {
        id: "tag-9",
        name: "marketing",
        description: "マーケティング関連",
        color: "#ec4899",
      },
      {
        id: "tag-10",
        name: "feedback",
        description: "顧客フィードバック",
        color: "#84cc16",
      },
      {
        id: "tag-11",
        name: "infrastructure",
        description: "インフラ関連",
        color: "#64748b",
      },
      {
        id: "tag-12",
        name: "documentation",
        description: "ドキュメント作成",
        color: "#a855f7",
      },
      {
        id: "tag-13",
        name: "business",
        description: "ビジネス関連",
        color: "#14b8a6",
      },
      {
        id: "tag-14",
        name: "planning",
        description: "計画・企画",
        color: "#f97316",
      },
      {
        id: "tag-15",
        name: "research",
        description: "リサーチ・調査",
        color: "#0ea5e9",
      },
      {
        id: "tag-16",
        name: "ux",
        description: "UX関連",
        color: "#6366f1",
      },
    ],
    terms: [
      {
        id: "term-1",
        key: "GTD",
        title: "Getting Things Done",
        description:
          "タスク管理手法の一つ。すべてのタスクを頭から出して外部システムで管理し、適切なタイミングで実行する手法。",
        status: "approved",
        sourceUrl:
          "https://ja.wikipedia.org/wiki/Getting_Things_Done",
        synonyms: ["gtd", "ゲッティング・シングス・ダン"],
        tags: ["planning"],
        createdAt: new Date(2025, 9, 1),
        updatedAt: new Date(2025, 9, 1),
      },
      {
        id: "term-2",
        key: "UI_UX",
        title:
          "ユーザーインターフェース/ユーザーエクスペリエンス",
        description:
          "UIは見た目や操作方法、UXはユーザーが製品を使う際の体験全体を指す。",
        status: "approved",
        sourceUrl: "https://example.com/ui_ux",
        synonyms: ["UI/UX", "ユーザビリティ"],
        tags: ["design", "ux"],
        createdAt: new Date(2025, 9, 5),
        updatedAt: new Date(2025, 9, 5),
      },
      {
        id: "term-3",
        key: "API",
        title: "Application Programming Interface",
        description:
          "ソフトウェア間でデータをやり取りするための仕組み。",
        status: "approved",
        sourceUrl: "https://example.com/api",
        synonyms: [
          "api",
          "アプリケーションプログラミングインターフェース",
        ],
        tags: ["development"],
        createdAt: new Date(2025, 9, 3),
        updatedAt: new Date(2025, 9, 3),
      },
      {
        id: "term-4",
        key: "CI_CD",
        title: "継続的インテグレーション/継続的デリバリー",
        description:
          "コードの変更を自動的にビルド・テスト・デプロイするプロセス。",
        status: "approved",
        sourceUrl: "https://example.com/ci_cd",
        synonyms: ["CI/CD", "継続的デプロイ"],
        tags: ["development", "infrastructure"],
        createdAt: new Date(2025, 9, 7),
        updatedAt: new Date(2025, 9, 7),
      },
      {
        id: "term-5",
        key: "MVP",
        title: "Minimum Viable Product",
        description:
          "最小限の機能を持った製品。市場投入して顧客からフィードバックを得るための初期バージョン。",
        status: "approved",
        synonyms: ["mvp", "最小実用製品"],
        tags: ["business", "planning"],
        createdAt: new Date(2025, 9, 8),
        updatedAt: new Date(2025, 9, 8),
      },
      {
        id: "term-6",
        key: "KPI",
        title: "Key Performance Indicator",
        description: "目標達成度を測るための重要な指標。",
        status: "approved",
        synonyms: ["kpi", "重要業績評価指標"],
        tags: ["business"],
        createdAt: new Date(2025, 9, 6),
        updatedAt: new Date(2025, 9, 6),
      },
      {
        id: "term-7",
        key: "LEGACY_CODE",
        title: "レガシーコード",
        description: "古い技術で書かれた、保守が困難なコード。",
        status: "deprecated",
        synonyms: ["legacy", "古いコード"],
        tags: ["development"],
        createdAt: new Date(2025, 8, 15),
        updatedAt: new Date(2025, 9, 10),
      },
      {
        id: "term-8",
        key: "AGILE",
        title: "アジャイル開発",
        description:
          "短い開発サイクルを繰り返し、顧客のフィードバックを取り入れながら開発を進める手法。",
        status: "approved",
        sourceUrl: "https://example.com/agile",
        synonyms: ["agile", "スクラム"],
        tags: ["planning", "development"],
        createdAt: new Date(2025, 9, 2),
        updatedAt: new Date(2025, 9, 2),
      },
      {
        id: "term-9",
        key: "RESPONSIVE_DESIGN",
        title: "レスポンシブデザイン",
        description:
          "画面サイズに応じて表示を最適化するデザイン手法。",
        status: "draft",
        synonyms: ["responsive", "適応デザイン"],
        tags: ["design"],
        createdAt: new Date(2025, 9, 20),
        updatedAt: new Date(2025, 9, 20),
      },
      {
        id: "term-10",
        key: "REFACTORING",
        title: "リファクタリング",
        description:
          "コードの振る舞いを変えずに、内部構造を改善すること。",
        status: "approved",
        synonyms: ["refactor", "コード整理"],
        tags: ["development"],
        createdAt: new Date(2025, 9, 4),
        updatedAt: new Date(2025, 9, 4),
      },
    ],
  });

  const navigateTo = (screen: string, itemId?: string) => {
    setCurrentScreen(screen);
    if (itemId) {
      setSelectedItemId(itemId);
    }
  };

  const handleCreateMemo = (newMemo: Memo) => {
    setAppData((prev) => ({
      ...prev,
      memos: [newMemo, ...prev.memos],
    }));
  };

  const handleCreateTask = (newTask: Task) => {
    setAppData((prev) => ({
      ...prev,
      tasks: [newTask, ...prev.tasks],
    }));
  };

  const handleCreateProject = (newProject: Project) => {
    setAppData((prev) => ({
      ...prev,
      projects: [newProject, ...prev.projects],
    }));
  };

  const handleCreateTag = (newTag: Tag) => {
    setAppData((prev) => ({
      ...prev,
      tags: [...prev.tags, newTag],
    }));
  };

  const handleCreateTerm = (newTerm: Term) => {
    setAppData((prev) => ({
      ...prev,
      terms: [newTerm, ...prev.terms],
    }));
  };

  const handleUpdateTask = (updatedTask: Task) => {
    setAppData((prev) => ({
      ...prev,
      tasks: prev.tasks.map((t) =>
        t.id === updatedTask.id ? updatedTask : t,
      ),
    }));
  };

  const handleUpdateProject = (updatedProject: Project) => {
    setAppData((prev) => ({
      ...prev,
      projects: prev.projects.map((p) =>
        p.id === updatedProject.id ? updatedProject : p,
      ),
    }));
  };

  const handleUpdateTag = (updatedTag: Tag) => {
    setAppData((prev) => ({
      ...prev,
      tags: prev.tags.map((t) =>
        t.id === updatedTag.id ? updatedTag : t,
      ),
    }));
  };

  const handleUpdateTerm = (updatedTerm: Term) => {
    setAppData((prev) => ({
      ...prev,
      terms: prev.terms.map((t) =>
        t.id === updatedTerm.id ? updatedTerm : t,
      ),
    }));
  };

  const handleRequestAISuggestion = (memoId: string) => {
    setAppData((prev) => ({
      ...prev,
      memos: prev.memos.map((m) =>
        m.id === memoId
          ? {
              ...m,
              aiSuggestionStatus: "pending" as const,
              updatedAt: new Date(),
            }
          : m,
      ),
    }));

    // 実際のローカルAI処理のシミュレーション
    setTimeout(() => {
      setAppData((prev) => ({
        ...prev,
        memos: prev.memos.map((m) =>
          m.id === memoId
            ? {
                ...m,
                aiSuggestionStatus: "available" as const,
                processedAt: new Date(),
              }
            : m,
        ),
      }));
    }, 2000); // 2秒後にAI提案が利用可能になる
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case "home":
        return (
          <HomeScreen data={appData} navigateTo={navigateTo} />
        );
      case "create-memo":
        return (
          <CreateMemoScreen
            tags={appData.tags}
            navigateTo={navigateTo}
            onMemoCreate={handleCreateMemo}
          />
        );
      case "memos":
        return (
          <MemosScreen
            memos={appData.memos}
            tags={appData.tags}
            navigateTo={navigateTo}
            selectedMemoId={selectedItemId}
            onAISuggestionRequest={handleRequestAISuggestion}
          />
        );
      case "tasks":
        return (
          <TasksScreen
            tasks={appData.tasks}
            projects={appData.projects}
            memos={appData.memos}
            tags={appData.tags}
            navigateTo={navigateTo}
            selectedTaskId={selectedItemId}
            onTaskUpdate={handleUpdateTask}
            onTaskCreate={handleCreateTask}
          />
        );
      case "projects":
        return (
          <ProjectsScreen
            projects={appData.projects}
            tasks={appData.tasks}
            tags={appData.tags}
            navigateTo={navigateTo}
            selectedProjectId={selectedItemId}
            onProjectCreate={handleCreateProject}
            onProjectUpdate={handleUpdateProject}
          />
        );
      case "tags":
        return (
          <TagsScreen
            tags={appData.tags}
            data={appData}
            navigateTo={navigateTo}
            onTagCreate={handleCreateTag}
            onTagUpdate={handleUpdateTag}
          />
        );
      case "terms":
        return (
          <TermsScreen
            terms={appData.terms}
            tags={appData.tags}
            data={appData}
            navigateTo={navigateTo}
            onTermCreate={handleCreateTerm}
            onTermUpdate={handleUpdateTerm}
          />
        );
      case "weekly-review":
        return (
          <WeeklyReviewScreen
            data={appData}
            navigateTo={navigateTo}
          />
        );
      case "settings":
        return <SettingsScreen />;
      default:
        return (
          <HomeScreen data={appData} navigateTo={navigateTo} />
        );
    }
  };

  return (
    <SidebarProvider>
      <div className="flex h-screen w-screen overflow-hidden bg-neutral-50">
        <AppSidebar
          currentScreen={currentScreen}
          onNavigate={setCurrentScreen}
        />
        <main className="flex-1 overflow-auto">
          <div className="h-full">{renderScreen()}</div>
        </main>
      </div>
    </SidebarProvider>
  );
}