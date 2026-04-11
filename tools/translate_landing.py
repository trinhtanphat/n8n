#!/usr/bin/env python3
"""
VNSO N8N - Landing Page i18n Translation Generator

Generates locale JSON files for the docs/ landing page from the English source.
Uses a curated translation dictionary per language for accuracy.

Usage:
    python3 tools/translate_landing.py              # Generate all 19 languages
    python3 tools/translate_landing.py --lang zh ja  # Only specific languages
    python3 tools/translate_landing.py --check       # Verify all locale files exist & have all keys

The en.json is the source of truth. Each language has a manually curated
translation map below. To update: edit the TRANSLATIONS dict, then re-run.
"""

import json
import os
import sys
import argparse
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
LOCALES_DIR = DOCS_DIR / "locales"

# ─────────────────────────────────────────────
# Translation dictionaries for 19 target languages
# ─────────────────────────────────────────────

TRANSLATIONS = {
    "zh": {  # Chinese Simplified
        "nav.features": "功能特性", "nav.usecases": "应用场景", "nav.guide": "使用指南",
        "nav.enterprise": "企业版", "nav.api": "API", "nav.launch": "启动 N8N",
        "hero.badge": "企业版 • 全部功能已解锁",
        "hero.title": "自动化一切工作流程",
        "hero.desc": "连接400+应用，可视化拖拽构建工作流，使用VNSO N8N安全部署。",
        "hero.start": "🚀 立即开始", "hero.guide": "📖 查看指南",
        "hero.stat1": "内置集成", "hero.stat2": "无限工作流", "hero.stat3": "自托管 & 安全", "hero.stat4": "支持语言",
        "features.title": "核心功能", "features.desc": "自动化工作流程所需的一切",
        "features.f1.title": "400+ 集成", "features.f1.desc": "连接 Gmail、Slack、Telegram、Google Sheets、Notion、MySQL、PostgreSQL、REST API 等数百个应用。",
        "features.f2.title": "可视化拖拽", "features.f2.desc": "直观的可视化编辑器，无需编码。通过简单拖拽设计复杂工作流。",
        "features.f3.title": "多样触发器", "features.f3.desc": "通过 Webhook、Cron、邮件事件、Telegram 消息、数据库变更等触发。",
        "features.f4.title": "自托管 & 安全", "features.f4.desc": "本地部署，完全控制数据。支持 HTTPS、安全Cookie、MFA、SAML、LDAP、OIDC。",
        "features.f5.title": "自定义代码 & AI", "features.f5.desc": "编写自定义 JavaScript/Python。集成 OpenAI、LangChain、AI Agent 实现智能自动化。",
        "features.f6.title": "管理与监控", "features.f6.desc": "详细执行日志、编辑器内调试、版本控制、审计日志和洞察面板。",
        "enterprise.title": "企业版功能", "enterprise.desc": "全部企业版功能已解锁",
        "enterprise.saml": "SAML 2.0 提供商单点登录", "enterprise.ldap": "从 Active Directory/LDAP 同步用户",
        "enterprise.oidc": "OpenID Connect 现代身份验证", "enterprise.roles_title": "自定义角色",
        "enterprise.roles": "细粒度自定义角色权限", "enterprise.audit": "完整活动日志",
        "enterprise.source": "使用 Git 版本控制管理工作流", "enterprise.secrets": "集成 HashiCorp Vault、AWS Secrets Manager",
        "enterprise.insights": "详细图表跟踪工作流性能", "enterprise.projects_title": "团队项目",
        "enterprise.projects": "无限团队项目与协作", "enterprise.debug_title": "编辑器内调试",
        "enterprise.debug": "直接在可视化编辑器中调试工作流", "enterprise.vars_title": "变量",
        "enterprise.vars": "工作区共享变量", "enterprise.ai": "AI 助手帮助构建工作流",
        "usecases.title": "实际应用", "usecases.desc": "您可以立即构建的热门工作流",
        "usecases.u1.title": "智能聊天机器人", "usecases.u1.desc": "AI 聊天机器人自动回复，24/7 客户服务，集成 OpenAI GPT。",
        "usecases.u2.title": "自动化人事请求", "usecases.u2.desc": "接收请假申请 → 发送审批 → 更新考勤 → 通知结果。",
        "usecases.u3.title": "多平台数据同步", "usecases.u3.desc": "在 CRM、ERP、Google Sheets 之间同步数据，确保实时一致性。",
        "usecases.u4.title": "CI/CD 通知流水线", "usecases.u4.desc": "GitHub webhook → 构建 → 通过 Slack/Email 发送详细日志结果。",
        "usecases.u5.tag": "报告", "usecases.u5.title": "自动日报", "usecases.u5.desc": "收集指标 → 生成 PDF/Excel 报告 → 邮件发送给管理层。",
        "usecases.u6.title": "AI 文档处理", "usecases.u6.desc": "上传发票 → OCR + AI 提取 → 保存数据库 → 创建处理工单。",
        "guide.title": "5分钟快速入门", "guide.desc": "从登录到第一个工作流",
        "guide.s1.title": "登录 / 注册", "guide.s1.desc": "访问 n8n.vnso.vn，使用邮箱登录或创建新账号。",
        "guide.s2.title": "创建新工作流", "guide.s2.desc": "按 Ctrl+Alt+N 或点击「添加工作流」，给它一个描述性名称。",
        "guide.s3.title": "添加触发节点", "guide.s3.desc": "选择触发器：Webhook、Schedule、Email、Telegram... 第一个节点始终是触发器。",
        "guide.s4.title": "连接操作节点", "guide.s4.desc": "拖拽处理节点：发送邮件、调用API、处理数据。用线连接。",
        "guide.s5.title": "测试与调试", "guide.s5.desc": "点击「测试工作流」运行。查看每个节点的输出，在编辑器中调试。",
        "guide.s6.title": "激活与监控", "guide.s6.desc": "开启「Active」开关自动运行。在执行记录标签中监控。",
        "shortcuts.title": "常用快捷键", "shortcuts.key": "快捷键", "shortcuts.action": "操作",
        "shortcuts.new": "创建新工作流", "shortcuts.save": "保存工作流", "shortcuts.run": "运行工作流",
        "shortcuts.add": "添加新节点", "shortcuts.copy": "复制/粘贴节点", "shortcuts.undo": "撤销",
        "shortcuts.delete": "删除选中节点", "shortcuts.disable": "启用/禁用节点", "shortcuts.fit": "适应视图",
        "api.title": "REST API & Webhook", "api.desc": "通过 API 与任何系统集成",
        "footer.product": "产品", "footer.resources": "资源", "footer.tech": "技术", "footer.powered": "技术支持",
    },
    "ja": {  # Japanese
        "nav.features": "機能", "nav.usecases": "活用事例", "nav.guide": "ガイド",
        "nav.enterprise": "エンタープライズ", "nav.api": "API", "nav.launch": "N8Nを開く",
        "hero.badge": "エンタープライズ版 • 全機能アンロック済み",
        "hero.title": "あらゆるワークフローを自動化",
        "hero.desc": "400以上のアプリを接続、ビジュアルなドラッグ＆ドロップでワークフローを構築、VNSO N8Nで安全にデプロイ。",
        "hero.start": "🚀 今すぐ始める", "hero.guide": "📖 ガイドを見る",
        "hero.stat1": "組み込み連携", "hero.stat2": "無制限ワークフロー", "hero.stat3": "セルフホスト＆安全", "hero.stat4": "対応言語",
        "features.title": "主な機能", "features.desc": "ワークフロー自動化に必要なすべて",
        "features.f1.title": "400以上の連携", "features.f1.desc": "Gmail、Slack、Telegram、Google Sheets、Notion、MySQL、PostgreSQL、REST APIなど数百のアプリと接続。",
        "features.f2.title": "ビジュアルドラッグ＆ドロップ", "features.f2.desc": "直感的なビジュアルエディタ、コード不要。シンプルなドラッグ＆ドロップで複雑なワークフローを設計。",
        "features.f3.title": "多様なトリガー", "features.f3.desc": "Webhook、Cron、メールイベント、Telegramメッセージ、データベース変更などでトリガー。",
        "features.f4.title": "セルフホスト＆安全", "features.f4.desc": "オンプレミスデプロイ、完全なデータ制御。HTTPS、セキュアCookie、MFA、SAML、LDAP、OIDC対応。",
        "features.f5.title": "カスタムコード＆AI", "features.f5.desc": "JavaScript/Pythonカスタムコード。OpenAI、LangChain、AIエージェントでスマート自動化。",
        "features.f6.title": "管理＆監視", "features.f6.desc": "詳細な実行ログ、エディタ内デバッグ、バージョン管理、監査ログ、インサイトダッシュボード。",
        "enterprise.title": "エンタープライズ機能", "enterprise.desc": "全エンタープライズ機能をアンロック済み",
        "enterprise.saml": "SAML 2.0プロバイダーでシングルサインオン", "enterprise.ldap": "Active Directory/LDAPからユーザー同期",
        "enterprise.oidc": "OpenID Connectでモダン認証", "enterprise.roles_title": "カスタムロール",
        "enterprise.roles": "カスタムロールによる詳細な権限管理", "enterprise.audit": "コンプライアンスのための完全な活動ログ",
        "enterprise.source": "Gitバージョン管理でワークフロー管理", "enterprise.secrets": "HashiCorp Vault、AWS Secrets Manager連携",
        "enterprise.insights": "詳細なチャートでワークフローパフォーマンス追跡", "enterprise.projects_title": "チームプロジェクト",
        "enterprise.projects": "無制限のチームプロジェクト＆コラボレーション", "enterprise.debug_title": "エディタ内デバッグ",
        "enterprise.debug": "ビジュアルエディタで直接ワークフローをデバッグ", "enterprise.vars_title": "変数",
        "enterprise.vars": "ワークスペース全体の共有変数", "enterprise.ai": "ワークフロー構築を支援するAIアシスタント",
        "usecases.title": "実際の活用事例", "usecases.desc": "今すぐ構築できる人気ワークフロー",
        "usecases.u1.title": "スマートチャットボット", "usecases.u1.desc": "AI自動応答チャットボット、24時間カスタマーケア、OpenAI GPT連携。",
        "usecases.u2.title": "人事リクエスト自動化", "usecases.u2.desc": "休暇申請受付→承認送信→勤怠更新→結果通知。",
        "usecases.u3.title": "マルチプラットフォームデータ同期", "usecases.u3.desc": "CRM、ERP、Google Sheets間でデータ同期、リアルタイム一貫性確保。",
        "usecases.u4.title": "CI/CD通知パイプライン", "usecases.u4.desc": "GitHub webhook→ビルド→Slack/Emailで詳細ログと結果送信。",
        "usecases.u5.tag": "レポート", "usecases.u5.title": "自動日報", "usecases.u5.desc": "メトリクス収集→PDF/Excelレポート生成→管理層にメール送信。",
        "usecases.u6.title": "AI文書処理", "usecases.u6.desc": "請求書アップロード→OCR+AI抽出→DB保存→処理チケット作成。",
        "guide.title": "5分で始める", "guide.desc": "ログインから最初のワークフローまで",
        "guide.s1.title": "ログイン/サインアップ", "guide.s1.desc": "n8n.vnso.vnにアクセス、メールでログインまたは新規アカウント作成。",
        "guide.s2.title": "新規ワークフロー作成", "guide.s2.desc": "Ctrl+Alt+Nまたは「ワークフロー追加」をクリック。わかりやすい名前を付ける。",
        "guide.s3.title": "トリガーノード追加", "guide.s3.desc": "トリガー選択：Webhook、Schedule、Email、Telegram...最初のノードは常にトリガー。",
        "guide.s4.title": "アクションノード接続", "guide.s4.desc": "処理ノードをドラッグ＆ドロップ：メール送信、API呼び出し、データ処理。ワイヤーで接続。",
        "guide.s5.title": "テスト＆デバッグ", "guide.s5.desc": "「ワークフローテスト」をクリックして実行。各ノードの出力確認、エディタ内デバッグ。",
        "guide.s6.title": "有効化＆監視", "guide.s6.desc": "「Active」トグルで自動実行。実行タブで監視。",
        "shortcuts.title": "便利なショートカット", "shortcuts.key": "ショートカット", "shortcuts.action": "アクション",
        "shortcuts.new": "新規ワークフロー作成", "shortcuts.save": "ワークフロー保存", "shortcuts.run": "ワークフロー実行",
        "shortcuts.add": "新規ノード追加", "shortcuts.copy": "コピー/ペースト", "shortcuts.undo": "元に戻す",
        "shortcuts.delete": "選択ノード削除", "shortcuts.disable": "ノード有効/無効", "shortcuts.fit": "ビューフィット",
        "api.title": "REST API & Webhook", "api.desc": "APIで任意のシステムと連携",
        "footer.product": "製品", "footer.resources": "リソース", "footer.tech": "テクノロジー", "footer.powered": "Powered by",
    },
    "ko": {  # Korean
        "nav.features": "기능", "nav.usecases": "활용 사례", "nav.guide": "가이드",
        "nav.enterprise": "엔터프라이즈", "nav.api": "API", "nav.launch": "N8N 열기",
        "hero.badge": "엔터프라이즈 에디션 • 모든 기능 잠금 해제",
        "hero.title": "모든 워크플로우를 자동화하세요",
        "hero.desc": "400개 이상의 앱 연결, 비주얼 드래그 앤 드롭으로 워크플로우 구축, VNSO N8N으로 안전하게 배포.",
        "hero.start": "🚀 시작하기", "hero.guide": "📖 가이드 보기",
        "hero.stat1": "내장 통합", "hero.stat2": "무제한 워크플로우", "hero.stat3": "셀프 호스팅 & 보안", "hero.stat4": "지원 언어",
        "features.title": "주요 기능", "features.desc": "워크플로우 자동화에 필요한 모든 것",
        "features.f1.title": "400+ 통합", "features.f1.desc": "Gmail, Slack, Telegram, Google Sheets, Notion, MySQL, PostgreSQL, REST API 등 수백 개 앱 연결.",
        "features.f2.title": "비주얼 드래그 앤 드롭", "features.f2.desc": "직관적인 비주얼 에디터, 코드 불필요. 간단한 드래그 앤 드롭으로 복잡한 워크플로우 설계.",
        "features.f3.title": "다양한 트리거", "features.f3.desc": "Webhook, Cron, 이메일 이벤트, Telegram 메시지, DB 변경 등으로 트리거.",
        "features.f4.title": "셀프 호스팅 & 보안", "features.f4.desc": "온프레미스 배포, 완전한 데이터 제어. HTTPS, 보안 쿠키, MFA, SAML, LDAP, OIDC 지원.",
        "features.f5.title": "커스텀 코드 & AI", "features.f5.desc": "JavaScript/Python 커스텀 코드. OpenAI, LangChain, AI Agent로 스마트 자동화.",
        "features.f6.title": "모니터링 & 관리", "features.f6.desc": "상세 실행 로그, 에디터 내 디버그, 버전 관리, 감사 로그, 인사이트 대시보드.",
        "enterprise.title": "엔터프라이즈 기능", "enterprise.desc": "모든 엔터프라이즈 기능 잠금 해제됨",
        "enterprise.saml": "SAML 2.0 제공자로 싱글 사인온", "enterprise.ldap": "Active Directory/LDAP에서 사용자 동기화",
        "enterprise.oidc": "OpenID Connect로 현대적 인증", "enterprise.roles_title": "커스텀 역할",
        "enterprise.roles": "커스텀 역할로 세밀한 권한 관리", "enterprise.audit": "규정 준수를 위한 완전한 활동 로그",
        "enterprise.source": "Git 버전 관리로 워크플로우 관리", "enterprise.secrets": "HashiCorp Vault, AWS Secrets Manager 통합",
        "enterprise.insights": "상세 차트로 워크플로우 성능 추적", "enterprise.projects_title": "팀 프로젝트",
        "enterprise.projects": "무제한 팀 프로젝트 & 협업", "enterprise.debug_title": "에디터 내 디버그",
        "enterprise.debug": "비주얼 에디터에서 직접 워크플로우 디버그", "enterprise.vars_title": "변수",
        "enterprise.vars": "전체 워크스페이스 공유 변수", "enterprise.ai": "워크플로우 구축을 돕는 AI 어시스턴트",
        "usecases.title": "실제 활용 사례", "usecases.desc": "지금 바로 구축할 수 있는 인기 워크플로우",
        "usecases.u1.title": "스마트 챗봇", "usecases.u1.desc": "AI 자동 응답 챗봇, 24/7 고객 관리, OpenAI GPT 통합.",
        "usecases.u2.title": "HR 요청 자동화", "usecases.u2.desc": "휴가 신청 접수 → 승인 전송 → 출근 업데이트 → 결과 알림.",
        "usecases.u3.title": "멀티 플랫폼 데이터 동기화", "usecases.u3.desc": "CRM, ERP, Google Sheets 간 데이터 동기화, 실시간 일관성 보장.",
        "usecases.u4.title": "CI/CD 알림 파이프라인", "usecases.u4.desc": "GitHub webhook → 빌드 → Slack/Email로 상세 로그 결과 전송.",
        "usecases.u5.tag": "보고서", "usecases.u5.title": "자동 일일 보고서", "usecases.u5.desc": "메트릭 수집 → PDF/Excel 보고서 생성 → 경영진에게 이메일 전송.",
        "usecases.u6.title": "AI 문서 처리", "usecases.u6.desc": "청구서 업로드 → OCR + AI 추출 → DB 저장 → 처리 티켓 생성.",
        "guide.title": "5분 만에 시작", "guide.desc": "로그인부터 첫 워크플로우까지",
        "guide.s1.title": "로그인 / 가입", "guide.s1.desc": "n8n.vnso.vn 방문, 이메일로 로그인 또는 새 계정 생성.",
        "guide.s2.title": "새 워크플로우 생성", "guide.s2.desc": "Ctrl+Alt+N 또는 '워크플로우 추가' 클릭. 설명적 이름 지정.",
        "guide.s3.title": "트리거 노드 추가", "guide.s3.desc": "트리거 선택: Webhook, Schedule, Email, Telegram... 첫 노드는 항상 트리거.",
        "guide.s4.title": "액션 노드 연결", "guide.s4.desc": "처리 노드 드래그 앤 드롭: 이메일 전송, API 호출, 데이터 처리. 와이어로 연결.",
        "guide.s5.title": "테스트 & 디버그", "guide.s5.desc": "'워크플로우 테스트' 클릭 실행. 노드별 출력 확인, 에디터 내 디버그.",
        "guide.s6.title": "활성화 & 모니터링", "guide.s6.desc": "'Active' 토글로 자동 실행. 실행 탭에서 모니터링.",
        "shortcuts.title": "유용한 단축키", "shortcuts.key": "단축키", "shortcuts.action": "동작",
        "shortcuts.new": "새 워크플로우 생성", "shortcuts.save": "워크플로우 저장", "shortcuts.run": "워크플로우 실행",
        "shortcuts.add": "새 노드 추가", "shortcuts.copy": "복사/붙여넣기", "shortcuts.undo": "실행 취소",
        "shortcuts.delete": "선택 노드 삭제", "shortcuts.disable": "노드 활성화/비활성화", "shortcuts.fit": "뷰 맞춤",
        "api.title": "REST API & Webhook", "api.desc": "API로 모든 시스템과 통합",
        "footer.product": "제품", "footer.resources": "리소스", "footer.tech": "기술", "footer.powered": "Powered by",
    },
    "fr": {  # French
        "nav.features": "Fonctionnalités", "nav.usecases": "Cas d'usage", "nav.guide": "Guide",
        "nav.enterprise": "Entreprise", "nav.api": "API", "nav.launch": "Lancer N8N",
        "hero.badge": "Édition Entreprise • Toutes les fonctionnalités déverrouillées",
        "hero.title": "Automatisez tous vos workflows",
        "hero.desc": "Connectez 400+ applications, construisez des workflows en glisser-déposer, déployez en toute sécurité avec VNSO N8N.",
        "hero.start": "🚀 Commencer", "hero.guide": "📖 Voir le guide",
        "hero.stat1": "Intégrations natives", "hero.stat2": "Workflows illimités", "hero.stat3": "Auto-hébergé & sécurisé", "hero.stat4": "Langues supportées",
        "features.title": "Fonctionnalités clés", "features.desc": "Tout ce dont vous avez besoin pour automatiser vos workflows",
        "features.f1.title": "400+ Intégrations", "features.f1.desc": "Connectez Gmail, Slack, Telegram, Google Sheets, Notion, MySQL, PostgreSQL, REST API et des centaines d'autres.",
        "features.f2.title": "Glisser-Déposer visuel", "features.f2.desc": "Éditeur visuel intuitif, sans code. Concevez des workflows complexes par simple glisser-déposer.",
        "features.f3.title": "Déclencheurs variés", "features.f3.desc": "Déclenchez par Webhook, Cron, événements email, messages Telegram, changements de base de données, et plus.",
        "features.f4.title": "Auto-hébergé & Sécurisé", "features.f4.desc": "Déploiement local, contrôle total des données. HTTPS, cookies sécurisés, MFA, SAML, LDAP, OIDC.",
        "features.f5.title": "Code personnalisé & IA", "features.f5.desc": "Écrivez du JavaScript/Python personnalisé. Intégrez OpenAI, LangChain, Agent IA pour l'automatisation intelligente.",
        "features.f6.title": "Surveillance & Gestion", "features.f6.desc": "Journaux d'exécution détaillés, débogage dans l'éditeur, contrôle de version, audit, tableau de bord insights.",
        "enterprise.title": "Fonctionnalités Entreprise", "enterprise.desc": "Toutes les fonctionnalités Enterprise déverrouillées",
        "enterprise.saml": "Connexion unique avec fournisseurs SAML 2.0", "enterprise.ldap": "Synchronisation utilisateurs depuis Active Directory/LDAP",
        "enterprise.oidc": "OpenID Connect pour l'authentification moderne", "enterprise.roles_title": "Rôles personnalisés",
        "enterprise.roles": "Permissions détaillées avec rôles personnalisés", "enterprise.audit": "Journalisation complète des activités",
        "enterprise.source": "Gestion des workflows avec Git", "enterprise.secrets": "Intégration HashiCorp Vault, AWS Secrets Manager",
        "enterprise.insights": "Suivi des performances avec graphiques détaillés", "enterprise.projects_title": "Projets d'équipe",
        "enterprise.projects": "Projets d'équipe illimités & collaboration", "enterprise.debug_title": "Débogage dans l'éditeur",
        "enterprise.debug": "Déboguez les workflows directement dans l'éditeur visuel", "enterprise.vars_title": "Variables",
        "enterprise.vars": "Variables partagées dans tout l'espace de travail", "enterprise.ai": "Assistant IA pour la construction de workflows",
        "usecases.title": "Cas d'utilisation réels", "usecases.desc": "Workflows populaires que vous pouvez créer immédiatement",
        "usecases.u1.title": "Chatbot Telegram intelligent", "usecases.u1.desc": "Chatbot IA pour réponses automatiques, service client 24/7, intégré avec OpenAI GPT.",
        "usecases.u2.title": "Demandes RH automatisées", "usecases.u2.desc": "Réception demande de congé → envoi approbation → mise à jour présence → notification résultat.",
        "usecases.u3.title": "Synchronisation multi-plateforme", "usecases.u3.desc": "Synchronisation entre CRM, ERP, Google Sheets, cohérence en temps réel.",
        "usecases.u4.title": "Pipeline de notifications CI/CD", "usecases.u4.desc": "Webhook GitHub → build → envoi résultats via Slack/Email avec logs détaillés.",
        "usecases.u5.tag": "Rapport", "usecases.u5.title": "Rapports quotidiens automatiques", "usecases.u5.desc": "Collecte métriques → génération rapport PDF/Excel → envoi email à la direction.",
        "usecases.u6.title": "Traitement de documents IA", "usecases.u6.desc": "Upload factures → OCR + IA extraction → sauvegarde BD → création ticket traitement.",
        "guide.title": "Démarrez en 5 minutes", "guide.desc": "De la connexion à votre premier workflow",
        "guide.s1.title": "Connexion / Inscription", "guide.s1.desc": "Visitez n8n.vnso.vn, connectez-vous par email ou créez un nouveau compte.",
        "guide.s2.title": "Créer un nouveau workflow", "guide.s2.desc": "Appuyez sur Ctrl+Alt+N ou cliquez 'Ajouter workflow'. Donnez-lui un nom descriptif.",
        "guide.s3.title": "Ajouter un nœud déclencheur", "guide.s3.desc": "Choisissez un déclencheur : Webhook, Schedule, Email, Telegram... Le premier nœud est toujours un déclencheur.",
        "guide.s4.title": "Connecter les nœuds d'action", "guide.s4.desc": "Glissez-déposez les nœuds de traitement : envoyer email, appeler API, traiter données. Connectez avec des fils.",
        "guide.s5.title": "Tester & Déboguer", "guide.s5.desc": "Cliquez 'Tester workflow' pour exécuter. Vérifiez la sortie par nœud, déboguez dans l'éditeur.",
        "guide.s6.title": "Activer & Surveiller", "guide.s6.desc": "Activez le toggle 'Active' pour l'exécution automatique. Surveillez dans l'onglet Exécutions.",
        "shortcuts.title": "Raccourcis utiles", "shortcuts.key": "Raccourci", "shortcuts.action": "Action",
        "shortcuts.new": "Créer nouveau workflow", "shortcuts.save": "Sauvegarder workflow", "shortcuts.run": "Exécuter workflow",
        "shortcuts.add": "Ajouter nouveau nœud", "shortcuts.copy": "Copier/Coller nœud", "shortcuts.undo": "Annuler",
        "shortcuts.delete": "Supprimer nœud sélectionné", "shortcuts.disable": "Activer/Désactiver nœud", "shortcuts.fit": "Ajuster la vue",
        "api.title": "REST API & Webhook", "api.desc": "Intégrez avec n'importe quel système via API",
        "footer.product": "Produit", "footer.resources": "Ressources", "footer.tech": "Technologie", "footer.powered": "Propulsé par",
    },
    "de": {  # German
        "nav.features": "Funktionen", "nav.usecases": "Anwendungsfälle", "nav.guide": "Anleitung",
        "nav.enterprise": "Enterprise", "nav.api": "API", "nav.launch": "N8N öffnen",
        "hero.badge": "Enterprise Edition • Alle Funktionen freigeschaltet",
        "hero.title": "Automatisieren Sie jeden Workflow",
        "hero.desc": "Verbinden Sie 400+ Apps, erstellen Sie visuelle Drag-and-Drop-Workflows, stellen Sie sicher mit VNSO N8N bereit.",
        "hero.start": "🚀 Jetzt starten", "hero.guide": "📖 Anleitung ansehen",
        "hero.stat1": "Integrierte Verbindungen", "hero.stat2": "Unbegrenzte Workflows", "hero.stat3": "Selbst gehostet & sicher", "hero.stat4": "Unterstützte Sprachen",
        "features.title": "Hauptfunktionen", "features.desc": "Alles was Sie für die Workflow-Automatisierung brauchen",
        "features.f1.title": "400+ Integrationen", "features.f1.desc": "Verbinden Sie Gmail, Slack, Telegram, Google Sheets, Notion, MySQL, PostgreSQL, REST API und hunderte mehr.",
        "features.f2.title": "Visuelles Drag & Drop", "features.f2.desc": "Intuitiver visueller Editor, kein Code erforderlich. Entwerfen Sie komplexe Workflows per Drag & Drop.",
        "features.f3.title": "Vielfältige Trigger", "features.f3.desc": "Auslösung per Webhook, Cron, E-Mail-Events, Telegram-Nachrichten, Datenbankänderungen und mehr.",
        "features.f4.title": "Selbst gehostet & Sicher", "features.f4.desc": "On-Premise-Bereitstellung, volle Datenkontrolle. HTTPS, sichere Cookies, MFA, SAML, LDAP, OIDC.",
        "features.f5.title": "Custom Code & KI", "features.f5.desc": "Schreiben Sie eigenen JavaScript/Python-Code. Integrieren Sie OpenAI, LangChain, KI-Agent für smarte Automatisierung.",
        "features.f6.title": "Überwachung & Verwaltung", "features.f6.desc": "Detaillierte Ausführungsprotokolle, Debugging im Editor, Versionskontrolle, Audit-Logs, Insights-Dashboard.",
        "enterprise.title": "Enterprise-Funktionen", "enterprise.desc": "Alle Enterprise-Funktionen freigeschaltet",
        "enterprise.saml": "Single Sign-On mit SAML 2.0 Anbietern", "enterprise.ldap": "Benutzer aus Active Directory/LDAP synchronisieren",
        "enterprise.oidc": "OpenID Connect für moderne Authentifizierung", "enterprise.roles_title": "Benutzerdefinierte Rollen",
        "enterprise.roles": "Detaillierte Berechtigungen mit benutzerdefinierten Rollen", "enterprise.audit": "Vollständige Aktivitätsprotokollierung",
        "enterprise.source": "Workflows mit Git-Versionskontrolle verwalten", "enterprise.secrets": "HashiCorp Vault, AWS Secrets Manager Integration",
        "enterprise.insights": "Workflow-Leistung mit detaillierten Diagrammen verfolgen", "enterprise.projects_title": "Teamprojekte",
        "enterprise.projects": "Unbegrenzte Teamprojekte & Zusammenarbeit", "enterprise.debug_title": "Debugging im Editor",
        "enterprise.debug": "Workflows direkt im visuellen Editor debuggen", "enterprise.vars_title": "Variablen",
        "enterprise.vars": "Gemeinsame Variablen für den gesamten Workspace", "enterprise.ai": "KI-Assistent beim Workflow-Aufbau",
        "usecases.title": "Praxisbeispiele", "usecases.desc": "Beliebte Workflows zum sofortigen Aufbau",
        "usecases.u1.title": "Intelligenter Chatbot", "usecases.u1.desc": "KI-Chatbot für automatische Antworten, 24/7 Kundenservice, OpenAI GPT integriert.",
        "usecases.u2.title": "Automatisierte HR-Anfragen", "usecases.u2.desc": "Urlaubsantrag empfangen → Genehmigung senden → Anwesenheit aktualisieren → Ergebnis benachrichtigen.",
        "usecases.u3.title": "Multi-Plattform-Datensynchronisation", "usecases.u3.desc": "Daten zwischen CRM, ERP, Google Sheets synchronisieren, Echtzeit-Konsistenz sicherstellen.",
        "usecases.u4.title": "CI/CD-Benachrichtigungspipeline", "usecases.u4.desc": "GitHub Webhook → Build → Ergebnisse via Slack/Email mit detaillierten Logs senden.",
        "usecases.u5.tag": "Bericht", "usecases.u5.title": "Automatische Tagesberichte", "usecases.u5.desc": "Metriken sammeln → PDF/Excel-Bericht erstellen → per E-Mail an Management senden.",
        "usecases.u6.title": "KI-Dokumentenverarbeitung", "usecases.u6.desc": "Rechnungen hochladen → OCR + KI-Extraktion → in DB speichern → Bearbeitungsticket erstellen.",
        "guide.title": "In 5 Minuten starten", "guide.desc": "Vom Login zum ersten Workflow",
        "guide.s1.title": "Anmelden / Registrieren", "guide.s1.desc": "Besuchen Sie n8n.vnso.vn, melden Sie sich per E-Mail an oder erstellen Sie ein neues Konto.",
        "guide.s2.title": "Neuen Workflow erstellen", "guide.s2.desc": "Drücken Sie Ctrl+Alt+N oder klicken Sie 'Workflow hinzufügen'. Geben Sie einen beschreibenden Namen.",
        "guide.s3.title": "Trigger-Node hinzufügen", "guide.s3.desc": "Trigger wählen: Webhook, Schedule, Email, Telegram... Der erste Node ist immer ein Trigger.",
        "guide.s4.title": "Action-Nodes verbinden", "guide.s4.desc": "Verarbeitungs-Nodes per Drag & Drop: E-Mail senden, API aufrufen, Daten verarbeiten. Mit Drähten verbinden.",
        "guide.s5.title": "Testen & Debuggen", "guide.s5.desc": "'Workflow testen' klicken. Ausgabe pro Node prüfen, im Editor debuggen.",
        "guide.s6.title": "Aktivieren & Überwachen", "guide.s6.desc": "'Active' Toggle für automatische Ausführung. Im Ausführungs-Tab überwachen.",
        "shortcuts.title": "Nützliche Tastenkürzel", "shortcuts.key": "Tastenkürzel", "shortcuts.action": "Aktion",
        "shortcuts.new": "Neuen Workflow erstellen", "shortcuts.save": "Workflow speichern", "shortcuts.run": "Workflow ausführen",
        "shortcuts.add": "Neuen Node hinzufügen", "shortcuts.copy": "Kopieren/Einfügen", "shortcuts.undo": "Rückgängig",
        "shortcuts.delete": "Ausgewählten Node löschen", "shortcuts.disable": "Node aktivieren/deaktivieren", "shortcuts.fit": "Ansicht anpassen",
        "api.title": "REST API & Webhook", "api.desc": "Integration mit jedem System über API",
        "footer.product": "Produkt", "footer.resources": "Ressourcen", "footer.tech": "Technologie", "footer.powered": "Unterstützt von",
    },
    "es": {  # Spanish
        "nav.features": "Características", "nav.usecases": "Casos de uso", "nav.guide": "Guía",
        "nav.enterprise": "Empresa", "nav.api": "API", "nav.launch": "Abrir N8N",
        "hero.badge": "Edición Enterprise • Todas las funciones desbloqueadas",
        "hero.title": "Automatiza cualquier flujo de trabajo",
        "hero.desc": "Conecta 400+ apps, construye workflows visuales con arrastrar y soltar, despliega de forma segura con VNSO N8N.",
        "hero.start": "🚀 Comenzar", "hero.guide": "📖 Ver guía",
        "hero.stat1": "Integraciones nativas", "hero.stat2": "Workflows ilimitados", "hero.stat3": "Auto-alojado y seguro", "hero.stat4": "Idiomas soportados",
        "features.title": "Características principales", "features.desc": "Todo lo que necesitas para automatizar tus workflows",
        "features.f1.title": "400+ Integraciones", "features.f1.desc": "Conecta Gmail, Slack, Telegram, Google Sheets, Notion, MySQL, PostgreSQL, REST API y cientos más.",
        "features.f2.title": "Arrastrar y soltar visual", "features.f2.desc": "Editor visual intuitivo, sin código. Diseña workflows complejos con simple arrastrar y soltar.",
        "features.f3.title": "Triggers diversos", "features.f3.desc": "Dispara por Webhook, Cron, eventos de email, mensajes de Telegram, cambios en BD, y más.",
        "features.f4.title": "Auto-alojado y seguro", "features.f4.desc": "Despliegue local, control total de datos. HTTPS, cookies seguras, MFA, SAML, LDAP, OIDC.",
        "features.f5.title": "Código personalizado e IA", "features.f5.desc": "Escribe JavaScript/Python personalizado. Integra OpenAI, LangChain, Agente IA para automatización inteligente.",
        "features.f6.title": "Monitoreo y gestión", "features.f6.desc": "Logs de ejecución detallados, depuración en editor, control de versiones, logs de auditoría, panel de insights.",
        "enterprise.title": "Funciones Enterprise", "enterprise.desc": "Todas las funciones Enterprise desbloqueadas",
        "enterprise.saml": "Inicio de sesión único con proveedores SAML 2.0", "enterprise.ldap": "Sincronizar usuarios desde Active Directory/LDAP",
        "enterprise.oidc": "OpenID Connect para autenticación moderna", "enterprise.roles_title": "Roles personalizados",
        "enterprise.roles": "Permisos detallados con roles personalizados", "enterprise.audit": "Registro completo de actividades",
        "enterprise.source": "Gestionar workflows con Git", "enterprise.secrets": "Integración con HashiCorp Vault, AWS Secrets Manager",
        "enterprise.insights": "Seguimiento del rendimiento con gráficos detallados", "enterprise.projects_title": "Proyectos de equipo",
        "enterprise.projects": "Proyectos de equipo ilimitados y colaboración", "enterprise.debug_title": "Depuración en editor",
        "enterprise.debug": "Depura workflows directamente en el editor visual", "enterprise.vars_title": "Variables",
        "enterprise.vars": "Variables compartidas en todo el workspace", "enterprise.ai": "Asistente IA para construir workflows",
        "usecases.title": "Casos de uso reales", "usecases.desc": "Workflows populares que puedes crear ahora mismo",
        "usecases.u1.title": "Chatbot inteligente", "usecases.u1.desc": "Chatbot IA para respuestas automáticas, atención al cliente 24/7, integrado con OpenAI GPT.",
        "usecases.u2.title": "Solicitudes RRHH automatizadas", "usecases.u2.desc": "Recibir solicitud de permiso → enviar aprobación → actualizar asistencia → notificar resultado.",
        "usecases.u3.title": "Sincronización multi-plataforma", "usecases.u3.desc": "Sincronizar datos entre CRM, ERP, Google Sheets, asegurando consistencia en tiempo real.",
        "usecases.u4.title": "Pipeline de notificaciones CI/CD", "usecases.u4.desc": "Webhook GitHub → build → enviar resultados por Slack/Email con logs detallados.",
        "usecases.u5.tag": "Informe", "usecases.u5.title": "Informes diarios automáticos", "usecases.u5.desc": "Recopilar métricas → generar informes PDF/Excel → enviar por email a dirección.",
        "usecases.u6.title": "Procesamiento de documentos IA", "usecases.u6.desc": "Subir facturas → OCR + IA extracción → guardar en BD → crear ticket de procesamiento.",
        "guide.title": "Empieza en 5 minutos", "guide.desc": "Desde el login hasta tu primer workflow",
        "guide.s1.title": "Iniciar sesión / Registrarse", "guide.s1.desc": "Visita n8n.vnso.vn, inicia sesión con email o crea una nueva cuenta.",
        "guide.s2.title": "Crear nuevo workflow", "guide.s2.desc": "Pulsa Ctrl+Alt+N o haz clic en 'Añadir workflow'. Dale un nombre descriptivo.",
        "guide.s3.title": "Añadir nodo trigger", "guide.s3.desc": "Elige trigger: Webhook, Schedule, Email, Telegram... El primer nodo siempre es un trigger.",
        "guide.s4.title": "Conectar nodos de acción", "guide.s4.desc": "Arrastra nodos de procesamiento: enviar email, llamar API, procesar datos. Conecta con cables.",
        "guide.s5.title": "Probar y depurar", "guide.s5.desc": "Haz clic en 'Probar workflow'. Ver salida por nodo, depurar en editor.",
        "guide.s6.title": "Activar y monitorear", "guide.s6.desc": "Activa el toggle 'Active' para ejecución automática. Monitorea en la pestaña Ejecuciones.",
        "shortcuts.title": "Atajos útiles", "shortcuts.key": "Atajo", "shortcuts.action": "Acción",
        "shortcuts.new": "Crear nuevo workflow", "shortcuts.save": "Guardar workflow", "shortcuts.run": "Ejecutar workflow",
        "shortcuts.add": "Añadir nuevo nodo", "shortcuts.copy": "Copiar/Pegar nodo", "shortcuts.undo": "Deshacer",
        "shortcuts.delete": "Eliminar nodo seleccionado", "shortcuts.disable": "Activar/Desactivar nodo", "shortcuts.fit": "Ajustar vista",
        "api.title": "REST API & Webhook", "api.desc": "Integra con cualquier sistema vía API",
        "footer.product": "Producto", "footer.resources": "Recursos", "footer.tech": "Tecnología", "footer.powered": "Desarrollado por",
    },
    "pt": {  # Portuguese
        "nav.features": "Recursos", "nav.usecases": "Casos de uso", "nav.guide": "Guia",
        "nav.enterprise": "Empresa", "nav.api": "API", "nav.launch": "Abrir N8N",
        "hero.badge": "Edição Enterprise • Todos os recursos desbloqueados",
        "hero.title": "Automatize qualquer fluxo de trabalho",
        "hero.desc": "Conecte 400+ apps, construa workflows visuais com arrastar e soltar, implante com segurança com VNSO N8N.",
        "hero.start": "🚀 Começar", "hero.guide": "📖 Ver guia",
        "hero.stat1": "Integrações nativas", "hero.stat2": "Workflows ilimitados", "hero.stat3": "Auto-hospedado e seguro", "hero.stat4": "Idiomas suportados",
        "features.title": "Recursos principais", "features.desc": "Tudo que você precisa para automatizar seus workflows",
        "features.f1.title": "400+ Integrações", "features.f1.desc": "Conecte Gmail, Slack, Telegram, Google Sheets, Notion, MySQL, PostgreSQL, REST API e centenas mais.",
        "features.f2.title": "Arrastar e soltar visual", "features.f2.desc": "Editor visual intuitivo, sem código. Projete workflows complexos com simples arrastar e soltar.",
        "features.f3.title": "Triggers diversos", "features.f3.desc": "Dispare por Webhook, Cron, eventos de email, mensagens Telegram, mudanças no BD, e mais.",
        "features.f4.title": "Auto-hospedado e seguro", "features.f4.desc": "Implantação local, controle total de dados. HTTPS, cookies seguros, MFA, SAML, LDAP, OIDC.",
        "features.f5.title": "Código personalizado e IA", "features.f5.desc": "Escreva JavaScript/Python personalizado. Integre OpenAI, LangChain, Agente IA para automação inteligente.",
        "features.f6.title": "Monitoramento e gestão", "features.f6.desc": "Logs de execução detalhados, debug no editor, controle de versão, logs de auditoria, painel de insights.",
        "enterprise.title": "Recursos Enterprise", "enterprise.desc": "Todos os recursos Enterprise desbloqueados",
        "enterprise.saml": "Single Sign-On com provedores SAML 2.0", "enterprise.ldap": "Sincronizar usuários do Active Directory/LDAP",
        "enterprise.oidc": "OpenID Connect para autenticação moderna", "enterprise.roles_title": "Papéis personalizados",
        "enterprise.roles": "Permissões detalhadas com papéis personalizados", "enterprise.audit": "Registro completo de atividades",
        "enterprise.source": "Gerenciar workflows com Git", "enterprise.secrets": "Integração HashiCorp Vault, AWS Secrets Manager",
        "enterprise.insights": "Acompanhar desempenho com gráficos detalhados", "enterprise.projects_title": "Projetos de equipe",
        "enterprise.projects": "Projetos de equipe ilimitados e colaboração", "enterprise.debug_title": "Debug no editor",
        "enterprise.debug": "Debug de workflows direto no editor visual", "enterprise.vars_title": "Variáveis",
        "enterprise.vars": "Variáveis compartilhadas em todo o workspace", "enterprise.ai": "Assistente IA para construir workflows",
        "usecases.title": "Casos de uso reais", "usecases.desc": "Workflows populares que você pode criar agora",
        "usecases.u1.title": "Chatbot inteligente", "usecases.u1.desc": "Chatbot IA para respostas automáticas, atendimento 24/7, integrado com OpenAI GPT.",
        "usecases.u2.title": "Solicitações RH automatizadas", "usecases.u2.desc": "Receber pedido de licença → enviar aprovação → atualizar presença → notificar resultado.",
        "usecases.u3.title": "Sincronização multi-plataforma", "usecases.u3.desc": "Sincronizar dados entre CRM, ERP, Google Sheets, garantindo consistência em tempo real.",
        "usecases.u4.title": "Pipeline de notificações CI/CD", "usecases.u4.desc": "Webhook GitHub → build → enviar resultados via Slack/Email com logs detalhados.",
        "usecases.u5.tag": "Relatório", "usecases.u5.title": "Relatórios diários automáticos", "usecases.u5.desc": "Coletar métricas → gerar relatórios PDF/Excel → enviar email para diretoria.",
        "usecases.u6.title": "Processamento de documentos IA", "usecases.u6.desc": "Upload faturas → OCR + IA extração → salvar no BD → criar ticket de processamento.",
        "guide.title": "Comece em 5 minutos", "guide.desc": "Do login ao seu primeiro workflow",
        "guide.s1.title": "Login / Cadastro", "guide.s1.desc": "Visite n8n.vnso.vn, faça login com email ou crie uma nova conta.",
        "guide.s2.title": "Criar novo workflow", "guide.s2.desc": "Pressione Ctrl+Alt+N ou clique em 'Adicionar workflow'. Dê um nome descritivo.",
        "guide.s3.title": "Adicionar nó trigger", "guide.s3.desc": "Escolha trigger: Webhook, Schedule, Email, Telegram... O primeiro nó é sempre um trigger.",
        "guide.s4.title": "Conectar nós de ação", "guide.s4.desc": "Arraste nós de processamento: enviar email, chamar API, processar dados. Conecte com fios.",
        "guide.s5.title": "Testar e debugar", "guide.s5.desc": "Clique 'Testar workflow'. Ver saída por nó, debugar no editor.",
        "guide.s6.title": "Ativar e monitorar", "guide.s6.desc": "Ative o toggle 'Active' para execução automática. Monitore na aba Execuções.",
        "shortcuts.title": "Atalhos úteis", "shortcuts.key": "Atalho", "shortcuts.action": "Ação",
        "shortcuts.new": "Criar novo workflow", "shortcuts.save": "Salvar workflow", "shortcuts.run": "Executar workflow",
        "shortcuts.add": "Adicionar novo nó", "shortcuts.copy": "Copiar/Colar nó", "shortcuts.undo": "Desfazer",
        "shortcuts.delete": "Excluir nó selecionado", "shortcuts.disable": "Ativar/Desativar nó", "shortcuts.fit": "Ajustar visualização",
        "api.title": "REST API & Webhook", "api.desc": "Integre com qualquer sistema via API",
        "footer.product": "Produto", "footer.resources": "Recursos", "footer.tech": "Tecnologia", "footer.powered": "Desenvolvido por",
    },
    "ru": {  # Russian
        "nav.features": "Функции", "nav.usecases": "Примеры", "nav.guide": "Руководство",
        "nav.enterprise": "Корпоративный", "nav.api": "API", "nav.launch": "Открыть N8N",
        "hero.badge": "Enterprise Edition • Все функции разблокированы",
        "hero.title": "Автоматизируйте любой рабочий процесс",
        "hero.desc": "Подключите 400+ приложений, создавайте визуальные процессы перетаскиванием, безопасно развертывайте с VNSO N8N.",
        "hero.start": "🚀 Начать", "hero.guide": "📖 Руководство",
        "hero.stat1": "Встроенных интеграций", "hero.stat2": "Неограниченные процессы", "hero.stat3": "Собственный хостинг", "hero.stat4": "Поддержка языков",
        "features.title": "Ключевые функции", "features.desc": "Всё необходимое для автоматизации рабочих процессов",
        "features.f1.title": "400+ Интеграций", "features.f1.desc": "Подключите Gmail, Slack, Telegram, Google Sheets, Notion, MySQL, PostgreSQL, REST API и сотни других.",
        "features.f2.title": "Визуальный редактор", "features.f2.desc": "Интуитивный визуальный редактор, без кода. Проектируйте сложные процессы простым перетаскиванием.",
        "features.f3.title": "Разнообразные триггеры", "features.f3.desc": "Запуск через Webhook, Cron, email-события, сообщения Telegram, изменения БД и другие.",
        "features.f4.title": "Собственный хостинг", "features.f4.desc": "Развертывание на своём сервере, полный контроль данных. HTTPS, безопасные cookie, MFA, SAML, LDAP, OIDC.",
        "features.f5.title": "Свой код и ИИ", "features.f5.desc": "Пишите JavaScript/Python. Интегрируйте OpenAI, LangChain, ИИ-агентов для умной автоматизации.",
        "features.f6.title": "Мониторинг и управление", "features.f6.desc": "Подробные логи выполнения, отладка в редакторе, контроль версий, аудит, панель аналитики.",
        "enterprise.title": "Корпоративные функции", "enterprise.desc": "Все корпоративные функции разблокированы",
        "enterprise.saml": "Single Sign-On с провайдерами SAML 2.0", "enterprise.ldap": "Синхронизация пользователей из AD/LDAP",
        "enterprise.oidc": "OpenID Connect для современной аутентификации", "enterprise.roles_title": "Пользовательские роли",
        "enterprise.roles": "Детальные разрешения с пользовательскими ролями", "enterprise.audit": "Полный журнал активности",
        "enterprise.source": "Управление процессами через Git", "enterprise.secrets": "Интеграция HashiCorp Vault, AWS Secrets Manager",
        "enterprise.insights": "Отслеживание производительности с графиками", "enterprise.projects_title": "Командные проекты",
        "enterprise.projects": "Неограниченные командные проекты", "enterprise.debug_title": "Отладка в редакторе",
        "enterprise.debug": "Отладка процессов прямо в редакторе", "enterprise.vars_title": "Переменные",
        "enterprise.vars": "Общие переменные для всего пространства", "enterprise.ai": "ИИ-помощник для создания процессов",
        "usecases.title": "Реальные примеры", "usecases.desc": "Популярные процессы, которые можно создать прямо сейчас",
        "usecases.u1.title": "Умный чат-бот", "usecases.u1.desc": "ИИ чат-бот с автоответами, обслуживание клиентов 24/7, интеграция OpenAI GPT.",
        "usecases.u2.title": "Автоматизация HR-запросов", "usecases.u2.desc": "Получение заявки на отпуск → согласование → обновление посещаемости → уведомление.",
        "usecases.u3.title": "Мультиплатформенная синхронизация", "usecases.u3.desc": "Синхронизация данных между CRM, ERP, Google Sheets в реальном времени.",
        "usecases.u4.title": "CI/CD уведомления", "usecases.u4.desc": "GitHub webhook → сборка → отправка результатов через Slack/Email с логами.",
        "usecases.u5.tag": "Отчёт", "usecases.u5.title": "Автоматические ежедневные отчёты", "usecases.u5.desc": "Сбор метрик → генерация PDF/Excel → отправка email руководству.",
        "usecases.u6.title": "ИИ обработка документов", "usecases.u6.desc": "Загрузка счетов → OCR + ИИ извлечение → сохранение в БД → создание задачи.",
        "guide.title": "Начните за 5 минут", "guide.desc": "От входа до первого процесса",
        "guide.s1.title": "Вход / Регистрация", "guide.s1.desc": "Перейдите на n8n.vnso.vn, войдите через email или создайте аккаунт.",
        "guide.s2.title": "Создать процесс", "guide.s2.desc": "Нажмите Ctrl+Alt+N или 'Добавить workflow'. Назовите описательно.",
        "guide.s3.title": "Добавить триггер", "guide.s3.desc": "Выберите триггер: Webhook, Schedule, Email, Telegram... Первый узел — всегда триггер.",
        "guide.s4.title": "Подключить узлы действий", "guide.s4.desc": "Перетащите узлы обработки: отправка email, вызов API, обработка данных. Соедините линиями.",
        "guide.s5.title": "Тест и отладка", "guide.s5.desc": "Нажмите 'Тестировать'. Проверьте вывод каждого узла, отладка в редакторе.",
        "guide.s6.title": "Активация и мониторинг", "guide.s6.desc": "Включите 'Active' для автозапуска. Мониторинг во вкладке Выполнения.",
        "shortcuts.title": "Полезные горячие клавиши", "shortcuts.key": "Клавиша", "shortcuts.action": "Действие",
        "shortcuts.new": "Создать процесс", "shortcuts.save": "Сохранить", "shortcuts.run": "Запустить",
        "shortcuts.add": "Добавить узел", "shortcuts.copy": "Копировать/Вставить", "shortcuts.undo": "Отменить",
        "shortcuts.delete": "Удалить узел", "shortcuts.disable": "Вкл/Выкл узел", "shortcuts.fit": "По размеру",
        "api.title": "REST API & Webhook", "api.desc": "Интеграция с любой системой через API",
        "footer.product": "Продукт", "footer.resources": "Ресурсы", "footer.tech": "Технологии", "footer.powered": "Работает на",
    },
}

# Simpler languages - derive from English with key translations
SIMPLE_TRANSLATIONS = {
    "ar": {"meta": "ar", "dir": "rtl", "translations": {
        "nav.features": "الميزات", "nav.usecases": "حالات الاستخدام", "nav.guide": "الدليل", "nav.enterprise": "المؤسسات", "nav.api": "API", "nav.launch": "فتح N8N",
        "hero.badge": "إصدار المؤسسات • جميع الميزات مفتوحة", "hero.title": "أتمتة أي سير عمل", "hero.desc": "اربط أكثر من 400 تطبيق، وابنِ سير عمل مرئي بالسحب والإفلات، وانشر بأمان مع VNSO N8N.",
        "hero.start": "🚀 ابدأ الآن", "hero.guide": "📖 عرض الدليل", "hero.stat1": "تكامل مدمج", "hero.stat2": "سير عمل غير محدود", "hero.stat3": "استضافة ذاتية وآمنة", "hero.stat4": "لغات مدعومة",
        "features.title": "الميزات الرئيسية", "features.desc": "كل ما تحتاجه لأتمتة سير العمل",
        "features.f1.title": "+400 تكامل", "features.f1.desc": "اربط Gmail وSlack وTelegram وGoogle Sheets وNotion وMySQL وPostgreSQL وREST API والمئات غيرها.",
        "features.f2.title": "سحب وإفلات مرئي", "features.f2.desc": "محرر مرئي بديهي، بدون كود. صمم سير عمل معقد بالسحب والإفلات البسيط.",
        "features.f3.title": "محفزات متنوعة", "features.f3.desc": "تشغيل بواسطة Webhook وCron وأحداث البريد ورسائل Telegram وتغييرات قاعدة البيانات.",
        "features.f4.title": "استضافة ذاتية وآمنة", "features.f4.desc": "نشر محلي، تحكم كامل بالبيانات. HTTPS، ملفات تعريف آمنة، MFA، SAML، LDAP، OIDC.",
        "features.f5.title": "كود مخصص وذكاء اصطناعي", "features.f5.desc": "اكتب JavaScript/Python. ادمج OpenAI وLangChain وعملاء AI للأتمتة الذكية.",
        "features.f6.title": "المراقبة والإدارة", "features.f6.desc": "سجلات تنفيذ مفصلة، تصحيح في المحرر، إدارة النسخ، سجلات التدقيق، لوحة التحليلات.",
        "enterprise.title": "ميزات المؤسسات", "enterprise.desc": "جميع ميزات المؤسسات مفتوحة",
        "guide.title": "ابدأ في 5 دقائق", "guide.desc": "من تسجيل الدخول إلى أول سير عمل",
        "shortcuts.title": "اختصارات مفيدة", "shortcuts.key": "اختصار", "shortcuts.action": "إجراء",
        "api.title": "REST API & Webhook", "api.desc": "التكامل مع أي نظام عبر API",
        "footer.product": "المنتج", "footer.resources": "الموارد", "footer.tech": "التقنية", "footer.powered": "مدعوم بواسطة",
    }},
    "hi": {"meta": "hi", "translations": {
        "nav.features": "विशेषताएं", "nav.usecases": "उपयोग", "nav.guide": "गाइड", "nav.enterprise": "एंटरप्राइज", "nav.api": "API", "nav.launch": "N8N खोलें",
        "hero.badge": "एंटरप्राइज संस्करण • सभी सुविधाएं अनलॉक", "hero.title": "किसी भी वर्कफ़्लो को स्वचालित करें",
        "hero.desc": "400+ ऐप्स कनेक्ट करें, विज़ुअल ड्रैग-एंड-ड्रॉप वर्कफ़्लो बनाएं, VNSO N8N के साथ सुरक्षित रूप से डिप्लॉय करें।",
        "hero.start": "🚀 शुरू करें", "hero.guide": "📖 गाइड देखें",
        "hero.stat1": "बिल्ट-इन इंटीग्रेशन", "hero.stat2": "असीमित वर्कफ़्लो", "hero.stat3": "सेल्फ-होस्टेड और सुरक्षित", "hero.stat4": "समर्थित भाषाएं",
        "features.title": "मुख्य विशेषताएं", "features.desc": "वर्कफ़्लो ऑटोमेशन के लिए सब कुछ",
        "enterprise.title": "एंटरप्राइज फीचर्स", "enterprise.desc": "सभी एंटरप्राइज फीचर्स अनलॉक",
        "guide.title": "5 मिनट में शुरू करें", "guide.desc": "लॉगिन से पहले वर्कफ़्लो तक",
        "shortcuts.title": "उपयोगी शॉर्टकट", "api.title": "REST API & Webhook",
        "footer.product": "उत्पाद", "footer.resources": "संसाधन", "footer.tech": "प्रौद्योगिकी", "footer.powered": "द्वारा संचालित",
    }},
    "th": {"meta": "th", "translations": {
        "nav.features": "คุณสมบัติ", "nav.usecases": "กรณีใช้งาน", "nav.guide": "คู่มือ", "nav.enterprise": "องค์กร", "nav.api": "API", "nav.launch": "เปิด N8N",
        "hero.badge": "Enterprise Edition • ปลดล็อกทุกฟีเจอร์", "hero.title": "อัตโนมัติทุกเวิร์กโฟลว์",
        "hero.desc": "เชื่อมต่อแอป 400+ รายการ สร้างเวิร์กโฟลว์แบบลากวาง ปรับใช้อย่างปลอดภัยกับ VNSO N8N",
        "hero.start": "🚀 เริ่มต้น", "hero.guide": "📖 ดูคู่มือ",
        "hero.stat1": "การเชื่อมต่อในตัว", "hero.stat2": "เวิร์กโฟลว์ไม่จำกัด", "hero.stat3": "โฮสต์เอง & ปลอดภัย", "hero.stat4": "ภาษาที่รองรับ",
        "features.title": "คุณสมบัติหลัก", "features.desc": "ทุกสิ่งที่คุณต้องการเพื่ออัตโนมัติเวิร์กโฟลว์",
        "enterprise.title": "ฟีเจอร์องค์กร", "enterprise.desc": "ปลดล็อกทุกฟีเจอร์องค์กร",
        "guide.title": "เริ่มต้นใน 5 นาที", "guide.desc": "จากล็อกอินสู่เวิร์กโฟลว์แรก",
        "shortcuts.title": "ทางลัดที่มีประโยชน์", "api.title": "REST API & Webhook",
        "footer.product": "ผลิตภัณฑ์", "footer.resources": "แหล่งข้อมูล", "footer.tech": "เทคโนโลยี", "footer.powered": "ขับเคลื่อนโดย",
    }},
    "id": {"meta": "id", "translations": {
        "nav.features": "Fitur", "nav.usecases": "Kasus Penggunaan", "nav.guide": "Panduan", "nav.enterprise": "Enterprise", "nav.api": "API", "nav.launch": "Buka N8N",
        "hero.badge": "Enterprise Edition • Semua Fitur Terbuka", "hero.title": "Otomatiskan semua alur kerja",
        "hero.desc": "Hubungkan 400+ aplikasi, buat workflow visual drag-and-drop, deploy dengan aman bersama VNSO N8N.",
        "hero.start": "🚀 Mulai Sekarang", "hero.guide": "📖 Lihat Panduan",
        "hero.stat1": "Integrasi bawaan", "hero.stat2": "Workflow tak terbatas", "hero.stat3": "Self-hosted & aman", "hero.stat4": "Bahasa didukung",
        "features.title": "Fitur Utama", "features.desc": "Semua yang Anda butuhkan untuk otomatisasi workflow",
        "enterprise.title": "Fitur Enterprise", "enterprise.desc": "Semua fitur Enterprise telah dibuka",
        "guide.title": "Mulai dalam 5 Menit", "guide.desc": "Dari login ke workflow pertama",
        "shortcuts.title": "Pintasan Berguna", "api.title": "REST API & Webhook",
        "footer.product": "Produk", "footer.resources": "Sumber Daya", "footer.tech": "Teknologi", "footer.powered": "Didukung oleh",
    }},
    "tr": {"meta": "tr", "translations": {
        "nav.features": "Özellikler", "nav.usecases": "Kullanım Alanları", "nav.guide": "Kılavuz", "nav.enterprise": "Kurumsal", "nav.api": "API", "nav.launch": "N8N'i Aç",
        "hero.badge": "Kurumsal Sürüm • Tüm Özellikler Açık", "hero.title": "Her iş akışını otomatikleştirin",
        "hero.desc": "400+ uygulama bağlayın, sürükle bırak ile görsel iş akışları oluşturun, VNSO N8N ile güvenle dağıtın.",
        "hero.start": "🚀 Başlayın", "hero.guide": "📖 Kılavuzu Gör",
        "hero.stat1": "Yerleşik entegrasyon", "hero.stat2": "Sınırsız iş akışı", "hero.stat3": "Self-hosted ve güvenli", "hero.stat4": "Desteklenen dil",
        "features.title": "Temel Özellikler", "features.desc": "İş akışı otomasyonu için ihtiyacınız olan her şey",
        "enterprise.title": "Kurumsal Özellikler", "enterprise.desc": "Tüm kurumsal özellikler açık",
        "guide.title": "5 Dakikada Başlayın", "guide.desc": "Girişten ilk iş akışınıza",
        "shortcuts.title": "Faydalı Kısayollar", "api.title": "REST API & Webhook",
        "footer.product": "Ürün", "footer.resources": "Kaynaklar", "footer.tech": "Teknoloji", "footer.powered": "Tarafından desteklenmektedir",
    }},
    "it": {"meta": "it", "translations": {
        "nav.features": "Funzionalità", "nav.usecases": "Casi d'uso", "nav.guide": "Guida", "nav.enterprise": "Enterprise", "nav.api": "API", "nav.launch": "Apri N8N",
        "hero.badge": "Edizione Enterprise • Tutte le funzionalità sbloccate", "hero.title": "Automatizza qualsiasi workflow",
        "hero.desc": "Collega 400+ app, crea workflow visivi con drag-and-drop, distribuisci in sicurezza con VNSO N8N.",
        "hero.start": "🚀 Inizia", "hero.guide": "📖 Vedi guida",
        "hero.stat1": "Integrazioni native", "hero.stat2": "Workflow illimitati", "hero.stat3": "Self-hosted e sicuro", "hero.stat4": "Lingue supportate",
        "features.title": "Funzionalità principali", "features.desc": "Tutto ciò che serve per automatizzare i tuoi workflow",
        "enterprise.title": "Funzionalità Enterprise", "enterprise.desc": "Tutte le funzionalità Enterprise sbloccate",
        "guide.title": "Inizia in 5 minuti", "guide.desc": "Dal login al primo workflow",
        "shortcuts.title": "Scorciatoie utili", "api.title": "REST API & Webhook",
        "footer.product": "Prodotto", "footer.resources": "Risorse", "footer.tech": "Tecnologia", "footer.powered": "Powered by",
    }},
    "nl": {"meta": "nl", "translations": {
        "nav.features": "Functies", "nav.usecases": "Toepassingen", "nav.guide": "Handleiding", "nav.enterprise": "Enterprise", "nav.api": "API", "nav.launch": "N8N openen",
        "hero.badge": "Enterprise Editie • Alle functies ontgrendeld", "hero.title": "Automatiseer elke workflow",
        "hero.desc": "Verbind 400+ apps, bouw visuele drag-and-drop workflows, implementeer veilig met VNSO N8N.",
        "hero.start": "🚀 Start nu", "hero.guide": "📖 Bekijk handleiding",
        "hero.stat1": "Ingebouwde integraties", "hero.stat2": "Onbeperkte workflows", "hero.stat3": "Self-hosted & veilig", "hero.stat4": "Ondersteunde talen",
        "features.title": "Belangrijkste functies", "features.desc": "Alles wat je nodig hebt voor workflow-automatisering",
        "enterprise.title": "Enterprise functies", "enterprise.desc": "Alle Enterprise functies ontgrendeld",
        "guide.title": "Start in 5 minuten", "guide.desc": "Van inloggen tot je eerste workflow",
        "shortcuts.title": "Handige sneltoetsen", "api.title": "REST API & Webhook",
        "footer.product": "Product", "footer.resources": "Bronnen", "footer.tech": "Technologie", "footer.powered": "Aangedreven door",
    }},
    "pl": {"meta": "pl", "translations": {
        "nav.features": "Funkcje", "nav.usecases": "Zastosowania", "nav.guide": "Przewodnik", "nav.enterprise": "Korporacja", "nav.api": "API", "nav.launch": "Otwórz N8N",
        "hero.badge": "Edycja Enterprise • Wszystkie funkcje odblokowane", "hero.title": "Zautomatyzuj każdy workflow",
        "hero.desc": "Połącz 400+ aplikacji, buduj wizualne workflow metodą przeciągnij-i-upuść, wdrażaj bezpiecznie z VNSO N8N.",
        "hero.start": "🚀 Rozpocznij", "hero.guide": "📖 Zobacz przewodnik",
        "hero.stat1": "Wbudowane integracje", "hero.stat2": "Nieograniczone workflow", "hero.stat3": "Self-hosted i bezpieczny", "hero.stat4": "Obsługiwane języki",
        "features.title": "Kluczowe funkcje", "features.desc": "Wszystko czego potrzebujesz do automatyzacji workflow",
        "enterprise.title": "Funkcje Enterprise", "enterprise.desc": "Wszystkie funkcje Enterprise odblokowane",
        "guide.title": "Zacznij w 5 minut", "guide.desc": "Od logowania do pierwszego workflow",
        "shortcuts.title": "Przydatne skróty", "api.title": "REST API & Webhook",
        "footer.product": "Produkt", "footer.resources": "Zasoby", "footer.tech": "Technologia", "footer.powered": "Napędzane przez",
    }},
    "uk": {"meta": "uk", "translations": {
        "nav.features": "Функції", "nav.usecases": "Приклади", "nav.guide": "Посібник", "nav.enterprise": "Корпоративний", "nav.api": "API", "nav.launch": "Відкрити N8N",
        "hero.badge": "Enterprise Edition • Усі функції розблоковано", "hero.title": "Автоматизуйте будь-який робочий процес",
        "hero.desc": "Підключіть 400+ додатків, створюйте візуальні процеси перетягуванням, безпечно розгортайте з VNSO N8N.",
        "hero.start": "🚀 Почати", "hero.guide": "📖 Переглянути посібник",
        "hero.stat1": "Вбудовані інтеграції", "hero.stat2": "Необмежені процеси", "hero.stat3": "Власний хостинг", "hero.stat4": "Підтримувані мови",
        "features.title": "Ключові функції", "features.desc": "Все необхідне для автоматизації робочих процесів",
        "enterprise.title": "Корпоративні функції", "enterprise.desc": "Усі корпоративні функції розблоковано",
        "guide.title": "Почніть за 5 хвилин", "guide.desc": "Від входу до першого процесу",
        "shortcuts.title": "Корисні гарячі клавіші", "api.title": "REST API & Webhook",
        "footer.product": "Продукт", "footer.resources": "Ресурси", "footer.tech": "Технології", "footer.powered": "Працює на",
    }},
    "sv": {"meta": "sv", "translations": {
        "nav.features": "Funktioner", "nav.usecases": "Användningsfall", "nav.guide": "Guide", "nav.enterprise": "Enterprise", "nav.api": "API", "nav.launch": "Öppna N8N",
        "hero.badge": "Enterprise Edition • Alla funktioner upplåsta", "hero.title": "Automatisera alla arbetsflöden",
        "hero.desc": "Anslut 400+ appar, bygg visuella dra-och-släpp-arbetsflöden, distribuera säkert med VNSO N8N.",
        "hero.start": "🚀 Kom igång", "hero.guide": "📖 Se guide",
        "hero.stat1": "Inbyggda integrationer", "hero.stat2": "Obegränsade arbetsflöden", "hero.stat3": "Självhostad & säker", "hero.stat4": "Språk som stöds",
        "features.title": "Nyckelfunktioner", "features.desc": "Allt du behöver för automatisering av arbetsflöden",
        "enterprise.title": "Enterprise-funktioner", "enterprise.desc": "Alla Enterprise-funktioner upplåsta",
        "guide.title": "Börja på 5 minuter", "guide.desc": "Från inloggning till ditt första arbetsflöde",
        "shortcuts.title": "Användbara genvägar", "api.title": "REST API & Webhook",
        "footer.product": "Produkt", "footer.resources": "Resurser", "footer.tech": "Teknik", "footer.powered": "Drivs av",
    }},
}


def flatten(d, parent_key="", sep="."):
    """Flatten nested dict to dot-notation keys."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten(d, sep="."):
    """Convert dot-notation dict back to nested dict."""
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        node = result
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    return result


def generate_locale(lang, trans_dict, en_flat):
    """Generate a locale JSON by merging English with translated strings."""
    merged = dict(en_flat)  # start with English as fallback
    for key, val in trans_dict.items():
        if key in merged:
            merged[key] = val
    return unflatten(merged)


def write_locale(lang, data):
    """Write a locale JSON file."""
    path = LOCALES_DIR / f"{lang}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def check_locales():
    """Verify all locale files exist and have the same keys as en.json."""
    en_path = LOCALES_DIR / "en.json"
    if not en_path.exists():
        print("ERROR: en.json not found!")
        return False

    with open(en_path, "r", encoding="utf-8") as f:
        en_data = json.load(f)
    en_keys = set(flatten(en_data).keys())

    all_langs = list(TRANSLATIONS.keys()) + list(SIMPLE_TRANSLATIONS.keys())
    ok = True
    for lang in sorted(all_langs):
        path = LOCALES_DIR / f"{lang}.json"
        if not path.exists():
            print(f"  MISSING: {lang}.json")
            ok = False
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        lang_keys = set(flatten(data).keys())
        missing = en_keys - lang_keys
        extra = lang_keys - en_keys
        status = "OK" if not missing else f"MISSING {len(missing)} keys"
        print(f"  {lang}: {status}")
        if missing:
            for k in sorted(missing)[:5]:
                print(f"    - {k}")
            ok = False
    return ok


def main():
    parser = argparse.ArgumentParser(description="Generate i18n locale files for VNSO N8N landing page")
    parser.add_argument("--lang", nargs="*", help="Only generate specific languages")
    parser.add_argument("--check", action="store_true", help="Check all locale files for completeness")
    parser.add_argument("--list", action="store_true", help="List available languages")
    args = parser.parse_args()

    if args.list:
        all_langs = sorted(set(list(TRANSLATIONS.keys()) + list(SIMPLE_TRANSLATIONS.keys())))
        print(f"Available languages ({len(all_langs)}):")
        for lang in all_langs:
            print(f"  {lang}")
        return

    if args.check:
        print("Checking locale files...")
        ok = check_locales()
        sys.exit(0 if ok else 1)

    LOCALES_DIR.mkdir(parents=True, exist_ok=True)

    # Load English source
    en_path = LOCALES_DIR / "en.json"
    with open(en_path, "r", encoding="utf-8") as f:
        en_data = json.load(f)
    en_flat = flatten(en_data)

    all_translations = {}
    all_translations.update(TRANSLATIONS)
    for lang, info in SIMPLE_TRANSLATIONS.items():
        all_translations[lang] = info["translations"]

    target_langs = args.lang if args.lang else list(all_translations.keys())
    generated = 0

    for lang in target_langs:
        if lang not in all_translations:
            print(f"  SKIP: {lang} - no translations defined")
            continue
        trans = all_translations[lang]
        locale_data = generate_locale(lang, trans, en_flat)
        path = write_locale(lang, locale_data)
        keys_translated = len(trans)
        keys_total = len(en_flat)
        pct = round(keys_translated / keys_total * 100)
        print(f"  {lang}: {path.name} ({keys_translated}/{keys_total} keys = {pct}%)")
        generated += 1

    print(f"\nGenerated {generated} locale files in {LOCALES_DIR}")
    print("Run with --check to verify completeness.")


if __name__ == "__main__":
    main()
