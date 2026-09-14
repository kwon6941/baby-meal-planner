# Baby Meal Planner

13개월 전후 아기 식단을 주간·월간으로 관리하고, 보유 재료 기반 추천과 실제 공개 레시피 링크를 연결하는 PWA입니다.

## 자동 레시피 DB 업데이트

- 앱 시작 시 `recipes.json`을 최신 상태로 불러옵니다.
- GitHub Actions가 매주 공개 유아식 레시피를 확인해 DB를 갱신합니다.
- 인터넷 연결이나 자동 DB 로딩이 실패하면 앱 내장 DB로 계속 동작합니다.
- Netlify를 이 저장소와 연결하면 DB 갱신 커밋 후 자동 재배포됩니다.

## 주요 파일

- `index.html`: 앱 본체
- `recipes.json`: 실제 레시피 DB
- `tools/update_recipes.py`: 레시피 DB 갱신 스크립트
- `.github/workflows/update-recipes.yml`: 매주 자동 갱신 작업
- `manifest.webmanifest`, `sw.js`: PWA 설정
