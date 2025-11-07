import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
} from "./ui/sidebar";
import {
  Home,
  FileText,
  CheckSquare,
  FolderOpen,
  Tag,
  CalendarCheck,
  Settings,
  BookOpen,
} from "lucide-react";

type AppSidebarProps = {
  currentScreen: string;
  onNavigate: (screen: string) => void;
};

export function AppSidebar({ currentScreen, onNavigate }: AppSidebarProps) {
  const menuItems = [
    { id: "home", icon: Home, label: "ホーム" },
    { id: "memos", icon: FileText, label: "メモ" },
    { id: "tasks", icon: CheckSquare, label: "タスク" },
    { id: "projects", icon: FolderOpen, label: "プロジェクト" },
    { id: "tags", icon: Tag, label: "タグ" },
    { id: "terms", icon: BookOpen, label: "社内用語" },
    { id: "weekly-review", icon: CalendarCheck, label: "週次レビュー" },
  ];

  return (
    <Sidebar>
      <SidebarHeader>
        <div className="flex items-center gap-2 px-4 py-3">
          <FileText className="size-6 text-blue-600" />
          <div>
            <div>Kage</div>
            <div className="text-neutral-500 text-xs">AI搭載のタスク管理アプリ</div>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>メニュー</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.id}>
                  <SidebarMenuButton
                    onClick={() => onNavigate(item.id)}
                    isActive={currentScreen === item.id}
                  >
                    <item.icon className="size-4" />
                    <span>{item.label}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              onClick={() => onNavigate("settings")}
              isActive={currentScreen === "settings"}
            >
              <Settings className="size-4" />
              <span>設定</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}