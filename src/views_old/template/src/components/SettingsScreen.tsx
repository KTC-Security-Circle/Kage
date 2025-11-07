import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Label } from "./ui/label";
import { Switch } from "./ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Separator } from "./ui/separator";
import { Button } from "./ui/button";
import { Settings, Bell, Palette, Database, Cpu, Info } from "lucide-react";

export function SettingsScreen() {
  return (
    <div className="p-8 space-y-6">
      <div>
        <h1>設定</h1>
        <p className="text-neutral-600 mt-2">アプリケーションの設定と環境設定</p>
      </div>

      <div className="max-w-3xl space-y-6">
        {/* ローカルAI設定 */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Cpu className="size-5 text-gray-600" />
              <CardTitle>ローカルAI設定</CardTitle>
            </div>
            <CardDescription>
              メモからタスクを生成するローカルAIの設定
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>AI自動処理</Label>
                <div className="text-sm text-neutral-500">
                  新しいメモを自動的にAIで処理する
                </div>
              </div>
              <Switch defaultChecked />
            </div>
            <Separator />
            <div className="space-y-2">
              <Label>AIモデル</Label>
              <Select defaultValue="local-llm-1">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="local-llm-1">ローカルLLM v1.0 (推奨)</SelectItem>
                  <SelectItem value="local-llm-2">ローカルLLM v2.0 (高精度)</SelectItem>
                  <SelectItem value="lightweight">軽量モデル (高速)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Separator />
            <div className="space-y-2">
              <Label>処理優先度</Label>
              <Select defaultValue="balanced">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="performance">パフォーマンス優先</SelectItem>
                  <SelectItem value="balanced">バランス (推奨)</SelectItem>
                  <SelectItem value="battery">バッテリー優先</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* 通知設定 */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Bell className="size-5 text-gray-600" />
              <CardTitle>通知設定</CardTitle>
            </div>
            <CardDescription>タスクとリマインダーの通知設定</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>デスクトップ通知</Label>
                <div className="text-sm text-neutral-500">
                  タスクのリマインダーを表示
                </div>
              </div>
              <Switch defaultChecked />
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>週次レビューの通知</Label>
                <div className="text-sm text-neutral-500">
                  毎週金曜日に週次レビューを促す
                </div>
              </div>
              <Switch defaultChecked />
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>AI処理完了の通知</Label>
                <div className="text-sm text-neutral-500">
                  メモのタスク生成が完了したときに通知
                </div>
              </div>
              <Switch defaultChecked />
            </div>
          </CardContent>
        </Card>

        {/* 外観設定 */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Palette className="size-5 text-gray-600" />
              <CardTitle>外観</CardTitle>
            </div>
            <CardDescription>アプリケーションの見た目を設定</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>テーマ</Label>
              <Select defaultValue="light">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">ライト</SelectItem>
                  <SelectItem value="dark">ダーク</SelectItem>
                  <SelectItem value="auto">システムに従う</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Separator />
            <div className="space-y-2">
              <Label>表示密度</Label>
              <Select defaultValue="comfortable">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="compact">コンパクト</SelectItem>
                  <SelectItem value="comfortable">快適 (推奨)</SelectItem>
                  <SelectItem value="spacious">ゆったり</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* データ管理 */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Database className="size-5 text-gray-600" />
              <CardTitle>データ管理</CardTitle>
            </div>
            <CardDescription>ローカルデータの管理とバックアップ</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>自動バックアップ</Label>
                <div className="text-sm text-neutral-500">
                  毎日自動的にデータをバックアップ
                </div>
              </div>
              <Switch defaultChecked />
            </div>
            <Separator />
            <div className="space-y-2">
              <Label>バックアップ先</Label>
              <div className="flex gap-2">
                <Button variant="outline" className="flex-1">
                  バックアップ先を選択
                </Button>
                <Button variant="outline">今すぐバックアップ</Button>
              </div>
            </div>
            <Separator />
            <div className="space-y-2">
              <Label>データのインポート/エクスポート</Label>
              <div className="flex gap-2">
                <Button variant="outline" className="flex-1">
                  データをエクスポート
                </Button>
                <Button variant="outline" className="flex-1">
                  データをインポート
                </Button>
              </div>
            </div>
            <Separator />
            <div className="space-y-2">
              <Label className="text-red-600">危険な操作</Label>
              <Button variant="destructive" className="w-full">
                すべてのデータを削除
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* アプリ情報 */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Info className="size-5 text-neutral-600" />
              <CardTitle>アプリ情報</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-neutral-600">バージョン</span>
              <span>1.0.0</span>
            </div>
            <Separator />
            <div className="flex justify-between text-sm">
              <span className="text-neutral-600">ビルド</span>
              <span>2025.10.22</span>
            </div>
            <Separator />
            <div className="flex justify-between text-sm">
              <span className="text-neutral-600">データベース</span>
              <span>ローカルストレージ</span>
            </div>
            <Separator />
            <div className="flex justify-between text-sm">
              <span className="text-neutral-600">AI モデル</span>
              <span>ローカルLLM v1.0</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
