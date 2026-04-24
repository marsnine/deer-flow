<p align="center">
  <a href="README.md">中文</a> · <b>한국어</b> · <a href="README.en.md">English</a>
</p>

<div align="center">

# Huashu Design (화수 디자인)

> *「타이핑. 엔터. 완성된 디자인을 바로 만나보세요.」*
> *"Type. Hit enter. A finished design lands in your lap."*

[![License](https://img.shields.io/badge/License-Personal%20Use%20Only-orange.svg)](LICENSE)
[![Agent-Agnostic](https://img.shields.io/badge/Agent-Agnostic-blueviolet)](https://skills.sh)
[![Skills](https://img.shields.io/badge/skills.sh-Compatible-green)](https://skills.sh)

<br>

**여러분의 에이전트에 한 문장만 입력하면, 즉시 전달 가능한 완성도 높은 디자인을 받을 수 있습니다.**

<br>

3분에서 30분이면 **제품 출시 애니메이션**, 클릭 가능한 App 프로토타입, 편집 가능한 PPT, 인쇄 가능한 고품질 인포그래픽을 완성할 수 있습니다.

"AI가 만든 것 치고는 괜찮네" 수준이 아닙니다. 대기업 디자인 팀에서 작업한 것 같은 퀄리티를 보장합니다. 스킬에 브랜드 에셋(로고, 색상 팔레트, UI 스크린샷 등)을 제공하면 브랜드의 고유한 분위기를 파악합니다. 아무것도 제공하지 않더라도 내장된 20가지 디자인 언어가 'AI스러운(slop)' 결과물을 피하도록 도와줍니다.

**이 README에 있는 모든 애니메이션은 huashu-design이 직접 제작했습니다.** Figma도, 애프터 이펙트도 아닙니다. 그저 한 줄의 프롬프트와 스킬 실행만으로 완성되었습니다. 다음 제품 출시 홍보 영상을 만들어야 하나요? 이제 여러분도 직접 만들 수 있습니다.

```
npx skills add alchaincyf/huashu-design
```

다양한 에이전트와 호환됩니다: Claude Code, Cursor, Codex, OpenClaw, Hermes 등에서 모두 사용할 수 있습니다.

[결과물 보기](#데모-갤러리) · [설치](#설치-및-사용) · [주요 기능](#주요-기능) · [핵심 메커니즘](#핵심-메커니즘) · [Claude Design과의 차이점](#claude-design과의-차이점)

</div>

---

<p align="center">
  <img src="https://github.com/alchaincyf/huashu-design/releases/download/v2.0/hero-animation-v10-en.gif" alt="huashu-design Hero" width="100%">
</p>

<p align="center"><sub>
  ▲ 25초 · 터미널 → 4가지 방향 → 갤러리 전환 → 4번의 포커스 → 브랜드 공개<br>
  👉 <a href="https://www.huasheng.ai/huashu-design-hero/">사운드가 포함된 HTML 인터랙티브 버전 보기</a> ·
  <a href="https://github.com/alchaincyf/huashu-design/releases/download/v2.0/hero-animation-v10-en.mp4">MP4 다운로드 (BGM+SFX 포함 · 10MB)</a>
</sub></p>

---

## 설치 및 사용

```bash
npx skills add alchaincyf/huashu-design
```

설치 후 Claude Code에서 바로 이야기하세요:

```
"AI 심리학 발표용 PPT를 만들어줘. 3가지 스타일 방향을 제안해 줘."
"AI 뽀모도로 타이머 iOS 프로토타입을 만들어줘. 4개의 핵심 화면은 실제로 클릭할 수 있어야 해."
"이 로직을 60초 애니메이션으로 만들고, MP4와 GIF로 내보내 줘."
"이 디자인에 대해 5가지 측면에서 전문가 리뷰를 해줘."
```

복잡한 버튼이나 패널, Figma 플러그인이 필요 없습니다.

---

## 스타 히스토리

<p align="center">
  <a href="https://star-history.com/#alchaincyf/huashu-design&Date">
    <img src="https://api.star-history.com/svg?repos=alchaincyf/huashu-design&type=Date" alt="huashu-design Star History" width="80%">
  </a>
</p>

---

## 주요 기능

| 기능 | 결과물 | 예상 소요 시간 |
|------|--------|----------|
| 인터랙티브 프로토타입 (App / Web) | 단일 파일 HTML · 실제 iPhone 베젤 · 클릭 가능 · Playwright 테스트 | 10–15분 |
| 프레젠테이션 (슬라이드) | HTML 덱 (브라우저 발표용) + 편집 가능한 PPTX (텍스트 박스 유지) | 15–25분 |
| 타임라인 애니메이션 | MP4 (25fps / 60fps 보간) + GIF (팔레트 최적화) + BGM | 8–12분 |
| 디자인 베리에이션 탐색 | 3개 이상의 비교 본 · Tweaks로 실시간 파라미터 조정 · 다양한 차원의 탐색 | 10분 |
| 인포그래픽 / 데이터 시각화 | 잡지 스타일의 타이포그래피 · PDF/PNG/SVG 내보내기 | 10분 |
| 디자인 방향 컨설턴트 | 5가지 학파 × 20가지 디자인 철학 · 3가지 방향 추천 · 병렬 데모 생성 | 5분 |
| 5차원 전문가 리뷰 | 방사형 차트 + 유지(Keep)/수정(Fix)/빠른 개선(Quick Wins) 리스트 제공 | 3분 |

---

## 데모 갤러리

### 디자인 방향 컨설턴트

요구사항이 명확하지 않을 때의 대체 솔루션입니다. 5가지 학파 × 20가지 디자인 철학 중에서 3가지 차별화된 방향을 선택하고, 사용자가 고를 수 있도록 병렬로 3개의 데모를 생성합니다.

<p align="center"><img src="https://github.com/alchaincyf/huashu-design/releases/download/v2.0/w3-fallback-advisor.gif" width="100%"></p>

### iOS App 프로토타입

iPhone 15 Pro의 정확한 기기 형태(다이내믹 아일랜드 / 상태 표시줄 / 홈 인디케이터) 제공 · 상태 기반의 다중 화면 전환 · Wikimedia/Met/Unsplash에서 실제 이미지 가져오기 · Playwright를 통한 자동 클릭 테스트.

<p align="center"><img src="https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c1-ios-prototype.gif" width="100%"></p>

### 모션 디자인 (Motion Design) 엔진

Stage + Sprite 기반의 타임라인 모델 · `useTime` / `useSprite` / `interpolate` / `Easing` 4가지 API로 모든 애니메이션 요구 충족 · 단일 명령어로 MP4 / GIF / 60fps 보간 / BGM 포함 최종 영상 내보내기.

<p align="center"><img src="https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c3-motion-design.gif" width="100%"></p>

### HTML 슬라이드 → 편집 가능한 PPTX

브라우저에서 진행하는 HTML 프레젠테이션 · `html2pptx.js`가 DOM의 computedStyle을 읽어 각 요소를 PowerPoint 객체로 변환 · 배경 이미지가 아닌 **실제 텍스트 박스**로 내보냅니다.

<p align="center"><img src="https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c2-slides-pptx.gif" width="100%"></p>

### Tweaks · 실시간 베리에이션 전환

색상 / 폰트 / 정보 밀도 등의 파라미터화 · 사이드 패널을 통한 전환 · 순수 프론트엔드 + `localStorage` 기반 상태 유지 · 새로고침해도 설정이 유지됩니다.

<p align="center"><img src="https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c4-tweaks.gif" width="100%"></p>

### 인포그래픽 / 데이터 시각화

잡지 수준의 레이아웃 · CSS Grid를 활용한 정밀한 단 나누기 · `text-wrap: pretty` 타이포그래피 디테일 · 실제 데이터 연동 · PDF 벡터 / 300dpi PNG / SVG 내보내기 지원.

<p align="center"><img src="https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c5-infographic.gif" width="100%"></p>

### 5차원 전문가 리뷰

디자인 철학 일관성 · 시각적 계층 구조 · 디테일 완성도 · 기능성 · 혁신성을 0-10점으로 평가 · 방사형 차트 시각화 · 유지(Keep) / 수정(Fix) / 빠른 개선(Quick Wins) 체크리스트 제공.

<p align="center"><img src="https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c6-expert-review.gif" width="100%"></p>

### 주니어 디자이너(Junior Designer) 워크플로우

무작정 결과물부터 만들지 않습니다. 먼저 가정(assumptions) + 임시 대체물(placeholders) + 이유(reasoning)를 작성하여 초기 단계에서 보여준 후 반복 개선합니다. 잘못된 방향으로 작업하는 것을 막아 수정 비용을 100배 줄일 수 있습니다.

<p align="center"><img src="https://github.com/alchaincyf/huashu-design/releases/download/v2.0/w2-junior-designer.gif" width="100%"></p>

### 브랜드 에셋 프로토콜 (5단계 필수 과정)

특정 브랜드의 작업 시 반드시 실행해야 하는 과정입니다: 질문 → 검색 → 다운로드(3가지 방법) → 색상 값 추출(grep) → `brand-spec.md` 작성.

<p align="center"><img src="https://github.com/alchaincyf/huashu-design/releases/download/v2.0/w1-brand-protocol.gif" width="100%"></p>

---

## 핵심 메커니즘

### 브랜드 에셋 프로토콜 (Brand Asset Protocol)

이 스킬에서 가장 엄격한 규칙입니다. 특정 브랜드(Stripe, Linear, Anthropic, 본인 회사 등) 작업 시 다음 5단계를 강제로 실행합니다:

| 단계 | 작업 내용 | 목적 |
|------|------|------|
| 1 · 질문 | 사용자가 브랜드 가이드라인을 가지고 있는지 확인 | 기존 리소스 존중 |
| 2 · 공식 페이지 검색 | `<brand>.com/brand` · `brand.<brand>.com` · `<brand>.com/press` | 정확한 브랜드 색상 추출 |
| 3 · 에셋 다운로드 | SVG 파일 → 공식 홈페이지 HTML 전체 → 제품 스크린샷에서 색상 추출 | 3가지 대안을 순차적으로 시도 |
| 4 · grep으로 색상 추출 | 에셋에서 모든 `#xxxxxx` 추출 후 빈도순 정렬, 무채색 필터링 | **기억에 의존하여 브랜드 색상 추측 금지** |
| 5 · 스펙 명문화 | `brand-spec.md` 파일 작성 + CSS 변수 생성, 모든 HTML에서 `var(--brand-*)` 사용 | 기록하지 않으면 잊어버림 방지 |

A/B 테스트 결과 (v1 vs v2, 각각 6개 에이전트 실행): **v2의 일관성 및 안정성이 v1보다 5배 높았습니다**. 이것이 이 스킬의 진정한 경쟁력입니다.

### 디자인 방향 컨설턴트 (Fallback 모드)

사용자의 요구사항이 모호하여 작업 시작이 어려울 때 실행됩니다:

- 흔한 디자인으로 대충 넘어가지 않고, Fallback 모드로 진입합니다.
- 5가지 학파 × 20가지 디자인 철학 중 **서로 다른 학파에서 3가지 방향**을 추천합니다.
- 각 방향에 대해 대표작, 고유의 분위기, 대표 디자이너를 함께 소개합니다.
- 사용자가 선택할 수 있도록 병렬로 3개의 시각 데모를 생성합니다.
- 방향이 결정되면 '주니어 디자이너 워크플로우' 본 과정으로 진입합니다.

### 주니어 디자이너 워크플로우 (Junior Designer Workflow)

모든 작업에 적용되는 기본 업무 방식입니다:

- 작업 시작 전 질문 리스트를 한 번에 보내고, 답변을 받은 후 진행합니다.
- HTML 파일에 가정(assumptions) + 임시 대체물(placeholders) + 주석(reasoning comments)을 먼저 작성합니다.
- 아주 초기 단계(회색 박스라도)에서 가능한 한 빨리 사용자에게 보여줍니다.
- 내용 채우기 → 베리에이션 생성 → Tweaks 설정 단계마다 다시 피드백을 받습니다.
- 최종 전달 전에 Playwright를 통해 브라우저에서 육안 검사를 진행합니다.

### AI Slop 방지 규칙

'전형적인 AI 결과물'처럼 보이는 요소를 피합니다 (보라색 그라데이션 / 이모지 남발 / 둥근 모서리와 왼쪽 테두리 포인트 / SVG 얼굴 드로잉 / Inter 폰트 남용). 대신 `text-wrap: pretty` + CSS Grid + 세심하게 선택된 Serif 폰트와 oklch 색상을 활용합니다.

---

## Claude Design과의 차이점

사실 브랜드 에셋 프로토콜의 철학은 Claude Design에서 알려진 프롬프트를 참고한 것입니다. 해당 프롬프트는 **"좋은 하이파이 디자인은 백지에서 시작하는 것이 아니라, 기존의 디자인 컨텍스트에서 자라나야 한다"**고 반복해서 강조합니다. 이 원칙이 65점짜리 결과물과 90점짜리 결과물을 가르는 기준이 됩니다.

포지셔닝 차이:

| | Claude Design | huashu-design |
|---|---|---|
| 형태 | 웹 제품 (브라우저 사용) | 스킬 (Claude Code 등에서 사용) |
| 제한 | 구독 할당량 (Quota) | API 사용량 · 병렬 에이전트 실행 시 할당량 제한 없음 |
| 결과물 | 캔버스 내 표시 + Figma 내보내기 | HTML / MP4 / GIF / 편집 가능 PPTX / PDF |
| 조작 방식 | GUI (클릭, 드래그, 수정) | 대화형 (채팅 입력 후 에이전트 작업 대기) |
| 복잡한 애니메이션 | 제한적 지원 | Stage + Sprite 타임라인 · 60fps 내보내기 지원 |
| 에이전트 호환성 | Claude.ai 전용 | 스킬을 지원하는 모든 에이전트 |

Claude Design은 **더 나은 그래픽 도구**라면, huashu-design은 **그래픽 도구라는 인터페이스 자체를 없애는 것**에 가깝습니다. 서로 다른 방향과 사용자를 대상으로 합니다.

---

## 제한 사항 (Limitations)

- **레이어 수준의 편집 가능한 PPTX를 Figma로 가져오기 미지원**: HTML을 생성하므로 스크린샷, 화면 녹화, 이미지 내보내기는 가능하지만, Keynote나 Figma로 드래그 앤 드롭하여 위치를 수정할 수는 없습니다.
- **Framer Motion 수준의 고난도 애니메이션 불가**: 3D, 물리 시뮬레이션, 파티클 시스템 등은 스킬의 한계를 벗어납니다.
- **브랜드 정보가 완전히 없는 경우 초기 디자인 품질이 60~65점 수준으로 하락**: 컨텍스트 없이 무에서 유를 창조하는 하이파이 작업은 최후의 수단입니다.

이것은 80점짜리 스킬이지, 100점짜리 완제품이 아닙니다. 하지만 그래픽 인터페이스를 직접 다루고 싶지 않은 사람에게는 100점짜리 제품보다 80점짜리 스킬이 훨씬 유용할 수 있습니다.

---

## 저장소 구조

```
huashu-design/
├── SKILL.md                 # 메인 문서 (에이전트 참조용)
├── README.md                # 본 문서 (사용자 열람용)
├── README.ko.md             # 한국어 README
├── README.en.md             # 영문 README
├── assets/                  # 기본 시작 컴포넌트(Starter Components)
│   ├── animations.jsx       # Stage + Sprite + Easing + interpolate
│   ├── ios_frame.jsx        # iPhone 15 Pro 베젤
│   ├── android_frame.jsx
│   ├── macos_window.jsx
│   ├── browser_window.jsx
│   ├── deck_stage.js        # HTML 슬라이드 엔진
│   ├── deck_index.html      # 멀티 파일 슬라이드 연결용
│   ├── design_canvas.jsx    # 베리에이션 나란히 보기
│   ├── showcases/           # 24가지 프리셋 샘플 (8개 시나리오 × 3가지 스타일)
│   └── bgm-*.mp3            # 6가지 시나리오별 배경음악
├── references/              # 태스크별 세부 가이드 문서
│   ├── animation-pitfalls.md
│   ├── design-styles.md     # 20가지 디자인 철학 라이브러리
│   ├── slide-decks.md
│   ├── editable-pptx.md
│   ├── critique-guide.md
│   ├── video-export.md
│   └── ...
├── scripts/                 # 내보내기 툴체인 (스크립트)
│   ├── render-video.js      # HTML → MP4
│   ├── convert-formats.sh   # MP4 → 60fps + GIF
│   ├── add-music.sh         # MP4 + BGM
│   ├── export_deck_pdf.mjs
│   ├── export_deck_pptx.mjs
│   ├── html2pptx.js
│   └── verify.py
└── demos/                   # 9가지 기능 시연 (c*/w*), 다국어 지원 GIF/MP4/HTML + hero v10
```

---

## 기원

Anthropic이 Claude Design을 발표한 날, 저는 새벽 4시까지 그것을 사용해 보았습니다. 하지만 며칠 뒤, 저는 그 툴을 다시 열지 않게 되었습니다. 제품이 별로여서가 아닙니다 (오히려 이 분야에서 가장 완성도 높은 제품입니다). 저는 GUI를 직접 조작하는 것보다, 터미널에서 에이전트가 알아서 일하도록 시키는 것을 더 선호했기 때문입니다.

그래서 에이전트에게 Claude Design 자체를 분석하도록 시켰습니다 (커뮤니티에 공개된 시스템 프롬프트, 브랜드 에셋 프로토콜, 컴포넌트 메커니즘 등 포함). 이를 구조화된 스펙(spec)으로 정제하고, 나만의 Claude Code에 사용할 수 있는 하나의 스킬(skill)로 재탄생시켰습니다.

Claude Design의 프롬프트를 명확하게 작성해 준 Anthropic에게 감사를 전합니다. 이런 다른 제품의 영감에 기반한 2차 창작이야말로, AI 시대 오픈소스 문화의 새로운 형태라고 생각합니다.

---

## 라이선스 · 사용 권한

**개인 사용 무료 및 자유** —— 학습, 연구, 창작, 개인 프로젝트, 블로그 글쓰기, 부업, SNS 업로드 등 원하는 곳에 언제든지 편하게 사용하세요.

**기업 및 상업적 사용 제한** —— 기업, 팀, 또는 영리 목적의 조직에서 본 스킬을 제품 연동, 외부 서비스 제공, 고객 프로젝트 등에 활용하고자 할 경우, **반드시 원작자(花生, Huasheng)에게 연락하여 별도의 라이선스를 취득해야 합니다.** 다음 사항이 포함되지만 이에 국한되지 않습니다:
- 사내 내부 툴체인 및 파이프라인의 일부로 활용하는 경우
- 고객에게 결과물을 납품하기 위한 주요 제작 도구로 사용하는 경우
- 이 스킬을 기반으로 2차 상업용 제품을 개발하는 경우
- 상업적 외주 프로젝트에 사용하는 경우

**상업적 사용 관련 문의**는 아래 SNS를 통해 연락 주시기 바랍니다.

---

## 연락처 · 花生 (Huasheng / 화수)

Huasheng은 AI 네이티브 개발자이자 인디 해커, AI 크리에이터입니다. 주요 프로젝트: 'Little Cat Fill Light' (앱스토어 유료 앱 1위), "DeepSeek 완벽 가이드북", Nüwa .skill (GitHub 12,000+ Star). 다중 플랫폼에서 30만 명 이상의 팔로워를 보유하고 있습니다.

| 플랫폼 | 계정명 | 링크 |
|---|---|---|
| X / Twitter | @AlchainHust | https://x.com/AlchainHust |
| WeChat (위챗) | 花叔 | 위챗에서 '花叔' 검색 |
| Bilibili | 花叔 | https://space.bilibili.com/14097567 |
| YouTube | 花叔 | https://www.youtube.com/@Alchain |
| Xiaohongshu | 花叔 | https://www.xiaohongshu.com/user/profile/5abc6f17e8ac2b109179dfdf |
| 홈페이지 | huasheng.ai | https://www.huasheng.ai/ |
| 개발자 페이지 | bookai.top | https://bookai.top |

상업적 사용 라이선스 취득, 제휴 문의 등은 위 플랫폼 중 편하신 곳으로 메시지를 남겨주세요.
