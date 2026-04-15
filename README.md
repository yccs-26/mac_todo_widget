# Todo Progress Widget 🚀

## 🇰🇷 한국어 

### 소개
**Todo Progress Widget**은 Mac 환경에서 사용할 수 있는 데스크톱 플로팅 위젯 앱입니다. 단순한 할 일 체크를 넘어, 각 작업의 **실제 달성률(0~150%)**을 드래그로 기록하고, 추후 데이터 분석을 위해 작업의 생성 시간과 체크 시간을 로컬 DB에 저장합니다.

### 주요 기능
* **즉각적인 추가 & 태그 시스템:** 위젯에서 바로 할 일을 추가할 수 있습니다. `태그) 할일` 형식으로 입력하면 추후 데이터 분석 시 카테고리화가 가능합니다.
* **150% 진행률 기록:** Todo 박스를 드래그하여 목표 초과 달성(최대 150%)까지 세밀하게 기록할 수 있습니다.
* **드래그 앤 드롭 순서 변경:** 자유롭게 할 일의 우선순위를 재배치할 수 있습니다.
* **스마트 숨김 기능:** 완료된 작업은 체크 즉시 숨김 처리되며, 위젯 전체를 축소하여 바탕화면을 깔끔하게 유지할 수 있습니다.
* **데이터 로깅:** 모든 활동(생성 시각, 체크 시각, 달성률)은 로컬 SQLite 데이터베이스에 기록되어, 이후 데이터 파이프라인 및 생산성 분석에 활용 가능합니다.

### 사용 방법
1. 저장소를 클론합니다: `git clone [repository URL]`
2. 필요 패키지를 설치합니다: `pip install -r requirements.txt`
3. 앱을 실행합니다: `python main.py`
4. 위젯 하단 입력창에 할 일을 입력하고 엔터를 누릅니다. (예: `python) 위젯 UI 개발`)

---

## 🇺🇸 English

### Overview
**Todo Progress Widget** is a floating desktop widget application for Mac. Beyond simple task checking, it allows users to record the **actual completion rate (0-150%)** of each task via drag interactions. It seamlessly logs creation and check times into a local database for future data analysis.

### Key Features
* **Quick Add & Tag System:** Add tasks directly from the widget. Use the format `tag) task` to easily categorize items for later analysis.
* **150% Progress Tracking:** Drag across the task box to record your exact progress, allowing for overachievement tracking up to 150%.
* **Drag and Drop Reordering:** Rearrange your to-do list effortlessly to match your priorities.
* **Smart Visibility:** Checked items are instantly hidden. The entire widget can be collapsed to keep your desktop clean.
* **Data Logging:** All actions (creation time, check time, progress rate) are saved in a local SQLite database, ready to be exported for productivity analysis or data engineering projects.

### How to Use
1. Clone the repository: `git clone [repository URL]`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`
4. Type your task in the input field at the bottom and press Enter. (e.g., `python) Develop widget UI`)