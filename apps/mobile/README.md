# PEG Scanner Mobile Application

This directory contains the React Native application for the PEG Scanner project. It provides the user interface for interacting with stock information, factor calculations, and the AI-powered conversational agent.

## How to Run

To run the mobile application, navigate to this directory and follow the standard React Native development procedures.

**Prerequisites:**
*   Node.js and npm/yarn
*   React Native development environment setup (including Android Studio, Xcode, CocoaPods for iOS)

**Commands (Example - may vary based on specific setup):**

```bash
# Install dependencies
npm install # or yarn install

# Type-check the React Native codebase
npx nx run mobile:typecheck

# Run on iOS (requires CocoaPods and Xcode)
npx react-native run-ios

# Run on Android (requires Android Studio and emulator/device)
npx react-native run-android
```

## Proto Integration

- The mobile app consumes protobuf payloads generated from `libs/schema/`. Descriptors are stored under `apps/mobile/src/proto/`.
  - `ping_descriptor.json` comes from `libs/schema/ping.proto`.
  - `single_stock_page_descriptor.json` mirrors `libs/schema/single_stock_page.proto` and powers the single-stock UI.
- Whenever a proto changes, regenerate the relevant descriptor(s):
  ```bash
  npx pbjs -t json -p libs/schema libs/schema/<file>.proto -o apps/mobile/src/proto/<file>_descriptor.json
  ```
- Protobuf decoding uses `protobufjs` with those descriptors so the UI renders the exact backend contracts (no ad-hoc JSON mapping).

## Single Stock Page

- The home screen now includes the single-stock detail module that fetches `SingleStockPageResponse` via protobuf.
- You can deep-link directly to a ticker using the `symbol` query param, e.g. `http://localhost:5173/?symbol=AAPL`.
- Use the “Load” input on the UI to jump to any symbol (even if it’s not currently listed in the PEG watchlist). The query param updates automatically so the page can be bookmarked or shared.
